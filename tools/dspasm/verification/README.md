# PowerBlocks DSPASM Verification
This is used to verify the output of PowerBlocks DSPASM for accuracy.

To begin verifying, with a known good version of PowerBlock DSPASM,
assemble the verification code.

```shell
dspasm_cli.py verify_ops.S -o verify_ops.bin
```

After making changes to DSPASM, verify it:
```shell
dspasm_verify.py verify_ops.S verify_ops.bin
```