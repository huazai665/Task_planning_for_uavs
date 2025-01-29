<template>
  <div
    class="home" 
    v-loading="loading"
    element-loading-text="消息发送中，请稍候"
    element-loading-spinner="el-icon-loading"
    element-loading-background="#1f2937"
  >
    <el-row :gutter="20" type="flex" justify="center" style="margin: 0 5% ">
      <el-col :span="18">
        <h1>广东省智能院&博维科技·具身智能平台</h1>
      </el-col>
      <el-col :span="6"></el-col>
    </el-row>
    <el-row :gutter="20" type="flex" justify="center" style="margin: 0 2% 0 5%; ">
      <el-col :span="18">
        <div class="ac-dialog-section">
          <div v-for="(item, index) in totalArr" :key="index">
            <div v-if="!(index % 2)" class="ac-user-dialog">
              <span>{{item}}</span>
            </div>

            <div v-if="index % 2" class="ac-robot-dialog">
              <span>{{item}}</span>
            </div>
          </div>

          <div v-if="ansLastList[0]">
            <el-form :model="ansLastForm">
              <el-form-item v-for="(item, index) in ansLastList" :key="index" class="ac-robot-dialog">
                  <span>{{item}}</span>
                  <div class="ac-ans-ins">                 
                    <el-button @click="operateDrone" type="text">启动无人机</el-button>
                    <el-divider direction="vertical"></el-divider>
                    <el-button @click="droneInstDialogVisible = true" type="text">修改指令</el-button>
                  </div>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <el-input
          class="ac-inst-input"
          type="textarea"
          :rows="4"
          placeholder="请输入内容"
          v-model="resultText">
        </el-input>

        <el-button class="ac-audio-button" @click="startAudio">语音</el-button>
        <br>
        <el-button class="ac-submit-button" @click="getInstruction">发送</el-button>
      </el-col>

      <el-col :span="6">
        <div  class="ac-mul-func">
          <div class="ac-function">功能：</div>
          <el-select v-model="selectedFunction">
            <el-option
              v-for="item in selectedFuncList"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>

          <div class="ac-model">模型：</div>
          <el-select v-model="selectedModel">
            <el-option
              v-for="item in selectedModelList"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </div>

        <el-button @click="clear" class="ac-clear" style="">清空对话</el-button>

      </el-col>
    </el-row>    


    <el-dialog
      title="语音输入"
      :visible.sync="dictationAudioDialogVisible"
      :close-on-click-modal="false"
      @close="closeDialog"
      class="audioDialog"
    >
      
      <div class="time-box">
        <span class="start-taste-line">
          <hr class="hr1" />
          <hr class="hr2" />
          <hr class="hr3" />
          <hr class="hr4" />
          <hr class="hr5" />
          <hr class="hr6" />
          <hr class="hr7" />
          <hr class="hr8" />
          <hr class="hr9" />
          <hr class="hr10" />
          <hr class="hr11" />
          <hr class="hr12" />
          <hr class="hr13" />
          <hr class="hr14" />
          <hr class="hr15" />
          <hr class="hr16" />
          <hr class="hr17" />
          <hr class="hr18" />
          <hr class="hr19" />
          <hr class="hr20" />
        </span>
      </div>
      <el-row style="margin-top:20px">
        <!-- <el-button icon="el-icon-video-play" @click="translationStart" round>开始</el-button> -->
        <el-button icon="el-icon-video-pause" @click="translationEnd" round>停止</el-button>

      </el-row >
      <div style="color:#fff;margin-top: 10px">{{timeSpan}}</div>
    </el-dialog>

    <el-dialog
      title="修改无人机指令"
      :visible.sync="droneInstDialogVisible"
      :close-on-click-modal="false"
      class="droneDialog"
    >
      <el-input
        type="textarea"
        :rows="20"
        placeholder="请输入内容"
        v-model="instructionText"
      >
      </el-input>

      <el-row style="margin-top: 15px">
        <el-button @click="droneInstDialogVisible = false">取消修改</el-button>
        <el-button @click="operateDrone">启动无人机</el-button>
      </el-row>
    </el-dialog>
  </div>
</template>

<script>
import Recorder from 'js-audio-recorder'
import IatRecorder from '../utils/IatRecorder.js'
import { getInstruction,operateDrone  } from '@/api/apis'
import { v4 as uuidv4 } from 'uuid';

export default {
  name: 'Home',
  components: {
  },
  data () {
    return {
      ansLastForm: {0:[]},
      ansLastList: [],
      hour: '00',
      minute: '00',
      second: 0,
      timeTemp: "",
      millisecond: 0,
      timeSpan: "00:00:00:00",
      selectedFunction: "UAV",
      selectedFuncList: [
        {label:"无人机控制", value: "UAV"}
      ],
      selectedModel: "chatmind_model",
      selectedModelList: [
        {label:"脑海模型", value: "chatmind_model"},
        {label:"openai", value: "openai_model"},
        {label:"chatglm", value: "chatglm_model"},
      ],
      // inputText: '',
      dictationAudioDialogVisible: false,
      droneInstDialogVisible: false,
      iatRecorder: '',
      appId: '3ed5503c',
      recorder: null,
      resultText: '',
      totalArr: [],
      sessionId: '',
      userName: 'asr-control',
      loading: false,
      instructionText: '',
      isInstructionHead: true,
      reqText: "",
      // instructionHead: `你是一个无人机控制中心，如果遇到需要执行的无人机命令，你会判断需要使用哪些指令。\n根据给定的任务，自动设计功能执行列表。\n每个指令()内有需要填的参数，则填入合适的数值。\n以id的取值可以是一个个体（1,2,...），可以为空()。\n同时执行多个无人机动作时，需要将代码放在with fly.sync_these():块中。\n\n以下是一些无人机指令：\nfly.takeoff(id) - 起飞第id号无人机。\nfly.land(id) - 降落第id号无人机。\nfly.left(x, id) - 第id号无人机向左飞x厘米。\nfly.right(x, id) - 第id号无人机向右飞x厘米。\nfly.forward(x, id) - 第id号无人机向前飞x厘米。\nfly.back(x, id) - 第id号无人机向后飞x厘米。\nfly.up(x, id) - 第id号无人机向上飞x厘米。\nfly.down(x, id) - 第id号无人机向下飞x厘米。\nfly.flip(dir, id) - 第id号无人机向dir方向翻转，dir的取值为'left'，'right'，'forward'，'back'。\nfly.rotate_cw(x, id) - 第id号无人机顺时针绕自身旋转x度，x取值范围为1-360度。\nfly.rotate_ccw(x, id) - 第id号无人机逆时针绕自身旋转x度，x取值范围为1-360度。\nfly.straight(x, y, z, s, id) - 第id号无人机以速度s cm/s直线飞行到坐标为（x,y,z）的目标地，x,y,z必须为整数值，单位为厘米，速度s 的取值范围为10-100cm/s。\nfly.curve(x1, y1, z1, x2, y2, z2, s, id) - 第id号无人机以速度s cm/s进行曲线飞行，该曲线经过三个点，分别为无人机当前位置点，曲线中间点(x1,y1,z1)和曲线终点(x2,y2,z2)，速度s的取值范围为10-100cm/s。\nfly.pause(x, id) - 暂停指定的t秒，然后继续。\nfly.wait_sync() - 阻塞等待前面无人机动作完成。\n\n用以下格式输出。\n示例：\n'''\n{\n\"指令\": [\"fly.takeoff()\"]\n}\n'''\n`,
      instructionHead: "你是一个无人机控制中心，如果遇到需要执行的无人机命令，你会判断需要使用哪些指令。\n根据给定的任务，自动设计功能执行列表。\n每个指令()内有需要填的参数，则填入合适的数值。\nid的取值可以是一个个体（1,2,...），默认所有无人机起飞则为'All'。\n同时执行多个无人机动作时，需要将代码放在with fly.sync_these():块中。\n\n以下是一些无人机指令：\nfly.takeoff(id) - 起飞。\nfly.land(id) - 降落。\nfly.left(x, id) - 向左飞x厘米。\nfly.right(x, id) - 向右飞x厘米。\nfly.forward(x, id) - 向前飞x厘米。\nfly.back(x, id) - 向后飞x厘米。\nfly.up(x, id) - 向上飞x厘米。\nfly.down(x, id) - 向下飞x厘米。\nfly.flip(dir, id) - 向dir方向翻转，dir的取值为'left'，'right'，'forward'，'back'。\nfly.rotate_cw(x, id) - 顺时针绕自身旋转x度，x取值范围为1-360度。\nfly.rotate_ccw(x, id) - 逆时针绕自身旋转x度，x取值范围为1-360度。\nfly.straight(x, y, z, s, id) - 以速度s cm/s直线飞行到坐标为（x,y,z）的目标地，x,y,z必须为整数值，单位为厘米，速度s 的取值范围为10-100cm/s。\nfly.curve(x1, y1, z1, x2, y2, z2, s, id) - 以速度s cm/s进行曲线飞行，该曲线经过三个点，分别为无人机当前位置点，曲线中间点(x1,y1,z1)和曲线终点(x2,y2,z2)，速度s的取值范围为10-100cm/s。\nfly.pause(x, id) - 暂停指定的t秒，然后继续。\nfly.wait_sync() - 阻塞等待前面动作完成。\n\n用以下格式输出。\n示例：\n```\n{\n  '指令': [\n    'fly.takeoff()'\n  ]\n}\n```\n"
    }
  },
  created () {
    this.recorder = new Recorder()
    this.iatRecorder = new IatRecorder('zh_cn', '', this.appId)
    this.sessionId = uuidv4()
    console.log("process.env:",process.env.ip)
  },
  watch: {
    selectedModel(newValue, oldValue) {
      console.log(oldValue,newValue)
      this.clear()
    }
  },
  methods: {
    Reset() {
      window.clearInterval(this.timeTemp);
      this.millisecond=this.hour=this.minute="00";
      this.second = 0
      this.millisecond = 0
      this.timeSpan='00:00:00:00';
    },
    start() {
      this.timeTemp=setInterval(this.timer,50);//每隔50毫秒执行一次timer函数
    },
    timer() {
      this.millisecond=this.millisecond+50;
      if(this.millisecond>=1000) {
        this.millisecond=0;
        this.second=this.second+1;
      }
      if(this.second>=60) {
        this.second=0;
        this.minute=this.minute+1;
      }

      if(this.minute>=60) {
        this.minute=0;
        this.hour=this.hour+1;
      }
      this.timeSpan=this.hour+':'+this.minute+':'+this.second+':'+this.millisecond+'';
    },
    operateDrone() {
      this.droneInstDialogVisible = false
      // let obj = this.judgeEmpty(this.instructionText)
      // if(!obj) {
      //   this.$message({
      //     message: '请输入有效指令',
      //     type: 'warning',
      //     duration: 2 * 1000
      //   })
      //   return
      // }
      this.loading = true
      this.ansLastList = []
      this.totalArr.push(this.instructionText)
      const param = {
        instruction: this.selectedModel === 'chatmind_model'? [this.instructionText] : this.instructionText
      }
      operateDrone(param).then(res=>{
        // if(res.status == 200) {
        //   this.$message.success("无人机操作成功。")
        // } else {
        //   this.$message.error("无人机操作失败。")
        // }
      }).catch(err => {
        console.log(err);
        this.$message.error(err)
      })
      this.loading = false
    },
    getInstruction() {
      if(this.ansLastList[0]) {
        return this.$message.warning("上一条无人机指令尚未发送")
      }
      this.loading = true
      if(this.selectedModel === 'chatmind_model') {      
        this.totalArr.push(this.resultText)
        const annotationObj = {
          content_list: this.totalArr,
          request_type: 0,
          sessionId: this.sessionId,
          userId: this.userName
        }
        getInstruction(annotationObj, this.selectedModel).then(res => {
          let response = res.data
          if(response.code == 200) {
            this.resultText = ""
            this.instructionText = response.response_list[0].replaceAll("```","")
            this.ansLastList.push(this.instructionText)
          } else {
            this.$message.error("暂时无法获取相应代码，请稍后重试。")
          }
          this.loading = false
        }).catch(err => {
          console.log(err);
          this.$message.error(err)
        });
      } else if(this.selectedModel === "openai_model") {        
        if(this.isInstructionHead) {
          this.reqText = this.instructionHead+"\n"+this.resultText
          this.isInstructionHead = false
        } else {
          this.reqText = this.resultText
        }

        this.totalArr.push(this.resultText)
        const annotationObj = {
          content: this.reqText
        }
        getInstruction(annotationObj, this.selectedModel).then(res => {
          console.log({res})
          if(res.data.content) {
            let response = res.data.content
            this.resultText = ""
            this.instructionText = response
            this.ansLastList.push(this.instructionText)
          } else {
            this.$message.error("暂时无法获取相应代码，请稍后重试。")
          }
          this.loading = false
        }).catch(err => {
          console.log(err);
          this.$message.error(err)
        });
      } else if(this.selectedModel === "chatglm_model") {
        const annotationObj = {
          content: this.resultText,
          content_list: this.totalArr,
        }
        getInstruction(annotationObj, this.selectedModel).then(res => {
          if(res.data) {
            this.totalArr.push(this.resultText)
            console.log("llm:",res.data)
            this.resultText = ""
            this.instructionText = res.data
            this.ansLastList.push(this.instructionText)
          } else {
            this.$message.error("暂时无法获取相应代码，请稍后重试。")
          }
          this.loading = false
        }).catch(err => {
          console.log(err);
          this.$message.error(err)
        });
      }
    },
    startAudio () {
      this.dictationAudioDialogVisible = true
      this.translationStart()
      this.start()
    },
    translationStart () {
      // this.recorder = new Recorder()
      console.log("start")
      this.iatRecorder = new IatRecorder('zh_cn', '', this.appId)
      this.iatRecorder.start();
    },
    translationEnd () {
      // debugger
      this.Reset()
      this.iatRecorder.onTextChange = (text) => {
        const inputText = text
        this.searchData = inputText.substring(0, inputText.length - 1)//  文字处理，因为不知道为什么识别输出的后面都带‘。’，这个方法是去除字符串最后一位
        console.log('this.searchData', this.searchData)
        this.resultText =this.searchData
        console.log('this.resultText', this.resultText)
        // this.translateResultText()
        this.dictationAudioDialogVisible = false
      }
    },
    closeDialog() {
      this.Reset()
      this.dictationAudioDialogVisible = false
    },
    judgeEmpty(str) {
      const val = str.replace(/\s*/g,"")
      return val
    },
    clear() {
      this.ansLastList = []
      this.resultText = ""
      this.totalArr = []
      this.sessionId = ""
      this.instructionText = ""
      this.isInstructionHead = true
      this.reqText = ""
    }
  }
}
</script>

<style lang="less" scoped>
.home {
  height: 100%;
}
:deep(.el-loading-spinner .el-loading-text){
  color: #ea580c;
}
:deep(.el-icon-loading){
  color: #ea580c;
}
.ac-dialog-section {
  overflow: auto;
  background:#1f2937;
  border-radius: 0.75rem;
  height: 550px;
  border: 1px solid #374151;

  .ac-user-dialog {
    text-align: left;
    align-items: center;
      // justify-content: center;
    margin: 28px auto 0 auto;
    min-height: 60px;
    // margin-bottom: 28px;
    line-height: 1.625;
    width: 94%;
    display: flex;
    background-color: #374151;
    border: 1px solid #4b5563;
    border-radius: 22px 22px 0 22px;
    float: right;
    margin-right: 5px;
    padding: 5px 15px;

  }
  .ac-user-dialog span {
    word-wrap: break-word;
    white-space: pre-wrap;
    width: 100%;
  }

  .ac-robot-dialog {
    text-align: left;
    align-items: center;
      // justify-content: center;
    margin: 28px auto 0 auto;
    min-height: 60px;
    // margin-bottom: 28px;
    line-height: 1.625;
    width: 94%;
    display: flex;
    background-color: #111827;
    border: 1px solid #4b5563;
    border-radius: 22px 22px 22px 0;
    float: left;
    margin-left: 5px;
    padding: 5px 15px;

  }
  .ac-robot-dialog span {
    word-wrap: break-word;
    white-space: pre-wrap;
    width: 100%;
  }

  .ac-ans-ins {
    float: right;
    margin-left: 10px;
  }
  .ac-ans-ins>.el-button {
    color: #ea580c;
  }
}
.ac-inst-input {
  :deep(.el-textarea__inner) {
    resize: none;
    border-radius: 0.75rem;
    margin: 20px 0;
    border:1px solid #374151;
    background: #1f2937;
    color: #fff;
  }
}

:deep(.el-input__inner) {
  background: #1f2937;
  border:1px solid #374151;
  box-shadow: rgba(0, 0, 0, 0.05) 0 1px 2px 0;
  color: #fff;
}

.ac-audio-button {
  border-radius: 0.75rem;
  width:  100%;
  background: linear-gradient(#4b5563, #374151);
  border:none;
  color:#fff
}

.ac-submit-button {
  border-radius: 0.75rem;
  width:100%;margin: 20px 0;
  background:#ea580c;
  border: none;
  color:#fff
}

.ac-mul-func {
  background:#1f2937;
  border-radius: 0.75rem;
  padding: 20px 20px 35px;
  border:1px solid #374151;

  .ac-function {
    text-align:left;
    margin-bottom:8px;
  }

  .ac-model {
    text-align:left;
    margin: 20px 0 8px;
  }

}
.ac-clear {
  border-radius: 0.75rem;
  width: 100%;
  background: linear-gradient(#4b5563, #374151);
  border: none;
  color:#fff;
  margin-top: 15px;
}

.audioDialog {
  :deep(.el-dialog) {
    background: #374151;
    .el-dialog__title {
      color: #fff;
    }
    .el-button {
      background:#ea580c;
      border: none;
      color: #fff;
    }
  }
}

.droneDialog {
  :deep(.el-dialog) {
    background: #374151;
    .el-dialog__title {
      color: #fff;
    }

    .el-button {
      background:#ea580c;
      border: none;
      color: #fff;
    }
  }

  :deep(.el-textarea__inner) {
    resize: none;
    border-radius: 0.75rem;
    margin: 20px 0;
    border:1px solid #374151;
    background: #1f2937;
    color: #fff;
  }
}


.ac-center {
  margin: 5% 8% !important;
  height:75vh;
}

.ac-input {
  height:90%;
  background:white;
  border-radius: 0.75rem;

  .el-textarea {
    height: 100%;
  }

  :deep(.el-textarea__inner) {
    border: none;
    height: 100%;
    border-radius: 0.75rem;
  }
}

.ac-button {
  margin-top: 15px
}

:deep(.el-dialog) {
  border-radius: 0.75rem !important;
}

.time-box .start-taste-line hr {
  background-color: #ea580c;  //声波颜色
  width: 6px;
  height: 12px;
  margin: 0 0.03rem;
  display: inline-block;
  border: none;
}
hr {
  animation: note 0.2s ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}
.hr1 {
  animation-delay: -1s;
}
.hr2 {
  animation-delay: -0.9s;
}
.hr3 {
  animation-delay: -0.8s;
}
.hr4 {
  animation-delay: -0.7s;
}
.hr5 {
  animation-delay: -0.6s;
}
.hr6 {
  animation-delay: -0.5s;
}
.hr7 {
  animation-delay: -0.4s;
}
.hr8 {
  animation-delay: -0.3s;
}
.hr9 {
  animation-delay: -0.2s;
}
.hr10 {
  animation-delay: -0.1s;
}
.hr11 {
  animation-delay: -1s;
}
.hr12 {
  animation-delay: -0.9s;
}
.hr13 {
  animation-delay: -0.8s;
}
.hr14 {
  animation-delay: -0.7s;
}
.hr15 {
  animation-delay: -0.6s;
}
.hr16 {
  animation-delay: -0.5s;
}
.hr17 {
  animation-delay: -0.4s;
}
.hr18 {
  animation-delay: -0.3s;
}
.hr19 {
  animation-delay: -0.2s;
}
.hr20 {
  animation-delay: -0.1s;
}
@keyframes note {
  from {transform: scaleY(1);}to {transform: scaleY(4);}
}
</style>
