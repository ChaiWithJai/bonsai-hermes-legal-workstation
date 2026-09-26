"""Record a queued integration check against an existing local model service."""
import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue-dir', type=Path, required=True)
    p.add_argument('--model-file', type=Path, required=True)
    p.add_argument('--server-binary', type=Path, required=True)
    p.add_argument('--server-pid', type=int, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--endpoint', default='http://127.0.0.1:62737/v1/chat/completions')
    args = p.parse_args()
    if urlparse(args.endpoint).hostname not in ('localhost', '127.0.0.1', '::1'): p.error('Use a local endpoint')
    if args.out.exists(): p.error('Output directory already exists')
    spec = importlib.util.spec_from_file_location('gpu_queue', args.queue_dir / 'gpu_queue.py')
    queue = importlib.util.module_from_spec(spec); spec.loader.exec_module(queue)
    job = 'legal-obligation-integration-' + str(time.time_ns())
    queue.put(job, 'mac', {'kind': 'resident-service-integration', 'runner_sha256': sha(Path(__file__))})
    if not queue.claim('mac', job):
        queue.update(job, 'blocked', 'Could not reserve Mac lane')
        raise SystemExit('Mac lane is held by another job')
    try:
        args.out.mkdir(parents=True)
        protocol = json.loads((HERE/'protocol.json').read_text())
        assert sha(HERE.parents[1]/protocol['source']) == protocol['source_sha256']
        manifest = {'queue_job': job, 'scope': 'Shared resident-service integration; not an isolated speed benchmark',
                    'model_sha256': sha(args.model_file), 'runtime_sha256': sha(args.server_binary),
                    'hardware': platform.platform(), 'processor': subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip(),
                    'launch_args': subprocess.check_output(['ps','-p',str(args.server_pid),'-o','args='],text=True).strip(),
                    'protocol': protocol, 'runner_sha256': sha(Path(__file__))}
        (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        import mlflow
        mlflow.set_tracking_uri('http://127.0.0.1:5210')
        mlflow.set_experiment('legal-obligation-response-limit')
        with mlflow.start_run(run_name=job) as run:
            mlflow.set_tags({'scope':'resident-service integration','human_acceptance':'pending','performance_comparison':'not_established'})
            for index, cap in enumerate((512,1024)):
                payload = json.loads((HERE/f'request-{cap}.json').read_text())
                assert hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest() == protocol['request_sha256'][index]
                with mlflow.start_span(name=f'local_completion_{cap}',span_type='LLM') as span:
                    span.set_inputs(payload)
                    start=time.monotonic()
                    req=urllib.request.Request(args.endpoint,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
                    with urllib.request.urlopen(req,timeout=180) as response: body=json.load(response)
                    elapsed=time.monotonic()-start
                    span.set_outputs(body)
                record={'request':payload,'response':body,'observed_seconds':elapsed}
                (args.out/f'response-{cap}.json').write_text(json.dumps(record,indent=2)+'\n')
                mlflow.log_metric(f'observed_seconds_{cap}',elapsed)
                print(json.dumps({'cap':cap,'finish_reason':body['choices'][0]['finish_reason'],'usage':body.get('usage')}),flush=True)
            mlflow.log_artifacts(str(args.out))
            (args.out/'mlflow.json').write_text(json.dumps({'run_id':run.info.run_id,'experiment_id':run.info.experiment_id},indent=2)+'\n')
        queue.update(job,'completed','Two resident-service requests captured; no performance or acceptance claim')
    except BaseException:
        queue.update(job,'needs_review','Integration interrupted; inspect request and server before retry')
        raise

if __name__ == '__main__': main()
