# Downloads

Every file the labs use, in one place. Small files live here; a recording over ~50 MB is linked from blob storage instead.

| File | What it is | |
|---|---|---|
| AOS command cheat sheet | every read-only command used in the labs | [Download](downloads/aos-show-cheatsheet.txt){ download } |
| `aos_readonly.py` | the read-only client the lab uses: allow-listed `show` commands over the AOS Web Services REST API ([Toolkit T.3](guides/toolkit.md#t3-the-read-only-client-aos_readonlypy)) | [Download](downloads/aos_readonly.py){ download } |
| `vc-pair.example.yml` | an HA pair declared as data: VLANs, bonds, checks ([Toolkit T.4](guides/toolkit.md#t4-the-desired-state-vc-pairexampleyml)) | [Download](downloads/vc-pair.example.yml){ download } |
| `fabric-as-code.example.yml` | the pipeline: plan on push, approved apply, daily drift ([Toolkit T.5](guides/toolkit.md#t5-the-pipeline-fabric-as-codeexampleyml)) | [Download](downloads/fabric-as-code.example.yml){ download } |

!!! note "Slides are PDF only"
    A `.pptx` carries the presenter's speaker notes, so slides are always published as a **PDF export**.
