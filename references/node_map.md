# 节点图谱 — 工作流 2105103613914865665《MiniMaxH3动作迁移 人物角色替换》

来源：2026-10-20 零扣费普查（哨兵字段法）＋首派成片内嵌 ComfyUI 图谱解码，双证一致。
源普查档：`~/workspace/probe_2112362746959458305/probe_2105103613914865665_census.md`

## 激活状态
- post/2105103613914865665：workflow 端点 **803 已激活**（派发用这个 ID）；ai-app 端点 901
- workflow/2112362746959458305（用户账号副本）：**810 未激活**，API 不可派

## 主链（MiniMax H3 Ref2VA 动作迁移）
- **8 LoadImage＝图片 1（唯一用户图槽）**：人物＋场景都认它
- **22 VHS_LoadVideo＝视频 1**：字段名 `video`；帧供动作参考、音轨直通输出
- 28 MiniMaxH3ReferenceToVideo：ref_image_0←17（图 1 缩放，最长边＝9 号原语，默认 1024，32 整除）；ref_video_0←26（视频帧裁到图 1 尺寸）；宽高←17 输出、长度←15
- 7 PrimitiveFloat 生成秒数（默认 10.0）＋12 fps=24 → 15 号公式总帧数＝round(秒×fps) 对齐 17k+5
- 提示词链（流内自带）：24 JoinStrings ＝ 20（10 动作替换词＋11 主体一致性词）＋ 18 AILab_QwenVL 对图 1 的自动描述（13 号描述提示词引导，≤160 字）。**手填 28.prompt 即整条替换此链**——本线靠手填写入「背景参考原片」句
- 其余：1 视频 VAE、2 音频 VAE（解码结果未进合成）、3 euler 采样选择、4 UNET minimax_h3_ref2va_int8_convrot、5 CLIP qwen3vl_32b、6 种子 8855、14 beta 调度 8 步、16 turbo LoRA（4 步）、21/25 Sage 注意力补丁、23 BEN2 抠图（产物未进主输出）、27 双图并排（仅预览）、29 Guider、30 SamplerCustomAdvanced、31/32 VAE 解码、**33 VHS_VideoCombine＝成片出口（mp4）**

## 残链（38–61，与主链无关，不要碰）
Anima/Qwen 生图残链：42 EmptyLatent 80×80、43 KSampler（seed 2943/cfg 4.5/er_sde/4 步）、45 固定文本、47 负词、48–61 一排 LoRA，唯一出口 46 solarL_SaveImagesToZip（80×80 图 ZIP）。每次结果集里那个 ZIP 就是它。46 号偶发通用 Exception 假失败 → 整单原样重派。

## 全流确认不存在
- `aspect_ratio` 字段、ref_image_*/ref_video_*/ref_audio_* 派发字段、`file` 视频字段、任何音频输入槽

## 显存实测（Standard，节点 30）
| 尺寸×帧 | 结果 |
|---|---|
| 1024×544 × 243 | ✅ 78 币（首派） |
| 576×1024 × 243（9:16×10 秒） | ✅ 72–85 币 |
| 576×768 × 464（3:4 全长） | ✅ 130 币 |
| 768×1024 × 464 | ❌ OOM |
| 768×1376 × 243 | ❌ OOM（另一次死于 46 号假失败） |
| 576×1024 × 464 | ❌ OOM |
