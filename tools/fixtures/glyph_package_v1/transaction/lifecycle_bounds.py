"""Check protocol 4 response maxima with independently generated Python protobuf."""
import importlib
from pathlib import Path
import subprocess
import sys
import tempfile

schema = Path(__file__).resolve().parents[4] / 'schema/haybox'
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, '-m', 'grpc_tools.protoc', '-I'+str(schema),
                    '--python_out='+tmp, str(schema/'config.proto'), str(schema/'package.proto')], check=True)
    sys.path.insert(0,tmp)
    pb = importlib.import_module('package_pb2')
    u32, u64 = 2**32-1, 2**64-1
    receipt = pb.PackageResponse(protocol_version=4, request_token=u64, status=1,
        store_generation=u32, profile_id=u32, profile_revision=u32, config_generation=u32,
        transaction_operation=17, transaction_token_high_water=u64, store_incarnation=u32,
        capability_version=2, logical=3, storage_floor=2, supported_package_format=1,
        supported_root_format=3,supported_record_format=2,supported_receipt_format=2,
        package_schema_version=1,max_create_request_bytes=4564,max_create_frame_bytes=4580,
        max_query_request_bytes=57,max_response_bytes=241,max_response_frame_bytes=244,
        row_index=29,rgb_index=30,semantic_digest=b'x'*32,config_sha=b'y'*32,record_sha=b'z'*32,
        max_query_frame_bytes=60,capability_bits=511,max_package_body_bytes=4491,
        record_publication_generation=u32,max_lifecycle_request_bytes=4580,max_lifecycle_frame_bytes=4601)
    assert len(receipt.SerializeToString(deterministic=True)) == receipt.max_response_bytes
    receipt.status, receipt.storage_floor, receipt.logical, receipt.write_fenced = 9,0,2,True
    assert receipt.ByteSize()==241 and receipt.ByteSize()+3==receipt.max_response_frame_bytes
    raw=1+receipt.max_lifecycle_request_bytes
    assert raw+(raw//254)+2==receipt.max_lifecycle_frame_bytes
    print('v4 terminal and fenced receipt bounds 241 bytes, framed 244; request bound 4580, framed 4601')
