<template>
  <div class="appContainer">
    <div class="pageTitle">
      <div class="sign" />
      <div class="listGroup">任务详情</div>
    </div>
    <el-button
      style="margin: 10px 0"
      size="small"
      type="primary"
      @click="openDialog('create')"
      >接受任务</el-button
    >
    <el-table
      :data="listData"
      element-loading-text="数据加载中，请稍后"
      fit
      :header-cell-style="headerCellStyle"
      :cell-style="cellClass"
    >
      <el-table-column label="姓名" align="center" prop="name">
        <template #default="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="性别" align="center">
        <template #default="scope">
          <span>{{ scope.row.sex }}</span>
        </template>
      </el-table-column>
      <el-table-column label="出生年月" align="center">
        <template #default="scope">
          {{ scope.row.birthDate }}
        </template>
      </el-table-column>
      <el-table-column label="身份证号码" align="center">
        <template #default="scope">
          {{ scope.row.idNumber }}
        </template>
      </el-table-column>
      <el-table-column label="电话号码" align="center">
        <template #default="scope">
          {{ scope.row.telephone }}
        </template>
      </el-table-column>
      <el-table-column label="电子邮箱" align="center">
        <template #default="scope">
          {{ scope.row.email }}
        </template>
      </el-table-column>
      <el-table-column label="人脸图片" align="center">
        <template #default="scope">
          <el-button type="text" @click="showClick" size="small"
            >查看</el-button
          >
        </template>
      </el-table-column>
      <el-table-column label="备注" align="center">
        <template #default="scope">
          {{ scope.row.memo }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" align="center" label="操作" width="200">
        <template #default="scope">
          <el-button
            type="text"
            size="small"
            @click="openDialog('edit', scope.row)"
            >修改</el-button
          >
          <el-button
            type="text"
            class="listDelBtn"
            @click="deleteMenu(scope.row)"
            >删除</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      class="rightPagination"
      current-page="1"
      page-size="1"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
    />

    <div v-dialogdrag>
      <el-dialog
        v-model="dialogFormVisible"
        width="1030px"
        :title="dialogTitleMap[openStatus]"
        :close-on-click-modal="false"
        @close="dialogClose"
      >
        <el-form
          ref="dataFormRef"
          :model="dataForm"
          label-width="100px"
          class="defaultForm"
          :rules="rules"
          label-position="right"
        >
          <div style="display: flex">
            <div style="width: 50%">
              <el-form-item label="姓名：" prop="name">
                <el-input
                  v-model.trim="dataForm.name"
                  type="text"
                  maxlength="7"
                  placeholder="请输入姓名"
                />
              </el-form-item>
              <el-form-item label="性别：" prop="sex">
                <el-radio-group v-model="dataForm.sex">
                  <el-radio :label="0">男</el-radio>
                  <el-radio :label="1">女</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="出生年月：" prop="birthDate">
                <el-date-picker
                  style="width: 100%"
                  v-model="dataForm.birthDate"
                  type="month"
                  placeholder="请输入出生年月"
                  :size="size"
                />
              </el-form-item>

              <el-form-item label="身份证号码：" prop="idNumber">
                <el-input
                  v-model.trim="dataForm.idNumber"
                  type="text"
                  placeholder="请输入身份证号码"
                />
              </el-form-item>

              <el-form-item label="电话号码：" prop="telephone">
                <el-input
                  v-model.trim="dataForm.telephone"
                  type="text"
                  placeholder="请输入电话号码"
                />
              </el-form-item>
              <el-form-item label="电子邮箱：" prop="email">
                <el-input
                  v-model.trim="dataForm.email"
                  type="text"
                  placeholder="请输入电子邮箱"
                />
              </el-form-item>
              <el-form-item label="所在省市：" prop="city">
                <el-cascader
                  style="width: 100%"
                  v-model="dataForm.city"
                  :options="options"
                  @change="handleChange"
                  placeholder="请选择所在省市"
                />
              </el-form-item>

              <el-form-item label="所在地址：" prop="address">
                <el-input
                  v-model.trim="dataForm.address"
                  type="text"
                  placeholder="请输入详细地址"
                />
              </el-form-item>
            </div>
            <div style="margin: 0 30px; border: 1px solid #dcdfe6"></div>
            <div style="width: 50%">
              <el-form-item label="学历：" prop="education">
                <el-select style="width: 100%" v-model="dataForm.education">
                  <el-option label="小学" :value="1" />
                  <el-option label="初中" :value="2" />
                  <el-option label="高中" :value="3" />
                  <el-option label="大专" :value="4" />
                  <el-option label="本科" :value="5" />
                  <el-option label="研究生" :value="6" />
                  <el-option label="博士" :value="7" />
                  <el-option label="中专" :value="8" />
                </el-select>
              </el-form-item>
              <el-form-item label="职业：" prop="occupation">
                <el-input
                  v-model.trim="dataForm.occupation"
                  placeholder="请填写职业"
                />
              </el-form-item>
              <el-form-item label="工作单位：" prop="occupation">
                <el-input
                  v-model.trim="dataForm.occupation"
                  placeholder="请填写工作单位"
                />
              </el-form-item>
              <el-form-item label="人脸图片：" prop="occupation">
                <el-input
                  style="width: 75%"
                  v-model.trim="dataForm.occupation"
                  placeholder="请上传人脸图片"
                />
                <el-upload
                  style="width: 10%; display: inline-block; margin-left: 20px"
                  class="upload-demo"
                  action="https://jsonplaceholder.typicode.com/posts/"
                  :before-upload="beforeUpload"
                  accept=".JPEG,.pic,.png"
                  :show-file-list="false"
                  :limit="1"
                  :file-list="dataForm.occupation"
                >
                  <el-button type="primary">上传</el-button>
                </el-upload>
                <div
                  style="font-size: 10px; line-height: 20px"
                  class="el-upload__tip"
                >
                  图片支持JPEG、JPG、PNG格式，大小不超过3MB，图像分辨率大于128×128像素，小于640×640像素。
                </div>
              </el-form-item>
              <el-form-item label="备注：" prop="memo">
                <el-input
                  style=""
                  v-model.trim="dataForm.memo"
                  placeholder="请填写备注"
                  type="textarea"
                  maxlength="100"
                  :rows="3"
                />
              </el-form-item>
            </div>
          </div>
        </el-form>
        <template #footer>
          <el-button @click="dialogClose">取消</el-button>
          <el-button type="primary" @click="submit()"> 确定</el-button>
        </template>
      </el-dialog>

      <el-drawer class="drawerBox" v-model="drawer" direction="rtl">
        <template #title>
          <div class="pageTitle">
            <div class="sign" />
            <div class="listGroup">查看</div>
          </div>
        </template>
        <div class="picbox">
          <div class="showpic">
            <img :src="picUrl" alt="" srcset="" />
          </div>
          <div class="picpanel"></div>
        </div>
        <ul style="list-style:none;padding:0">
          <li> 姓名：梁小敏</li>
          <li> 性别：女</li>
          <li>出生年月：1980年1月</li>
          <li>身份证号码：440123456789012324</li>
          <li>电话号码：13212345678</li>
          <li>电子邮箱：13212345678@163.com</li>
          <li>所在省市：广东省深圳市</li>
          <li>所在地址：</li>
          <li>学历：</li>
          <li>职业：</li>
          <li>工作单位：</li>
          <li>备注：</li>
          
        </ul>
      </el-drawer>
    </div>
  </div>
</template>
                  
<script>
import { reactive, toRefs } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'renwuziliaoluru',
  setup() {
    const state = reactive({
      drawer: false,
      listData: [
        {
          name: '梁小民',
          sex: '男',
          birthDate: '1998年1月',
          idNumber: '440123456789012324',
          telephone: '13512312312',
          email: '440123456789012324',
          memo: '-',
        },
        {
          name: '梁小敏',
          sex: '女',
          birthDate: '1999年5月',
          idNumber: '440123456781256478',
          telephone: '12345678911',
          email: '13212345678@163.com',
          memo: '-',
        },
      ],
      options: [
        {
          value: 'guide',
          label: 'Guide',
          children: [
            {
              value: 'disciplines',
              label: 'Disciplines',
              children: [
                {
                  value: 'consistency',
                  label: 'Consistency',
                },
                {
                  value: 'feedback',
                  label: 'Feedback',
                },
                {
                  value: 'efficiency',
                  label: 'Efficiency',
                },
                {
                  value: 'controllability',
                  label: 'Controllability',
                },
              ],
            },
            {
              value: 'navigation',
              label: 'Navigation',
              children: [
                {
                  value: 'side nav',
                  label: 'Side Navigation',
                },
                {
                  value: 'top nav',
                  label: 'Top Navigation',
                },
              ],
            },
          ],
        },
      ],
      pageSizeArr: [10, 20, 30], // 分数数量数组
      total: 10,

      dialogFormVisible: false,
      openStatus: '',
      dataForm: {
        sex: 1,
      },
      dialogTitleMap: {
        create: '资料录入',
        edit: '修改',
      },
    })
    const openDialog = async (status) => {
      state.openStatus = status
      if (status === 'edit') {
        state.dialogFormVisible = true
      } else {
        state.dialogFormVisible = true
      }
    }
    const dialogClose = async () => {
      state.dialogFormVisible = false
    }
    const submit = async () => {
      state.dialogFormVisible = false
    }
    const deleteMenu = () => {
      ElMessageBox.confirm('确定要删除吗？','提示',{
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
        .then(() => {})
        .catch(() => {
          // catch error
        })
    }
    const showClick = () => {
      state.drawer = true
    }
    return {
      ...toRefs(state),
      openDialog,
      dialogClose,
      submit,
      showClick,
      deleteMenu
    }
  },
}
</script>

<style lang="scss" scoped>
:deep(.el-drawer__body){
  overflow: auto;
}
:deep(.el-drawer__header) {
  margin-bottom: 0;
}
.picbox {
  position: relative;
  border: 1px solid rgba(25, 186, 139, 0.17);
  height: 300px;
  padding: 16px;
  .showpic {
    padding: 16px;
    height: 100%;
    width: 100%;
    text-align: center;
    background-color: rgb(245, 247, 249);
    width: 100%;
    overflow: auto;
    img {
      height: 220px;
    }
  }
  &::before {
    position: absolute;
    top: 0;
    left: 0;
    content: '';
    width: 10px;
    height: 10px;
    border-top: 2px solid #02a6b5;
    border-left: 2px solid #02a6b5;
  }
  &::after {
    position: absolute;
    top: 0;
    right: 0;
    content: '';
    width: 10px;
    height: 10px;
    border-top: 2px solid #02a6b5;
    border-right: 2px solid #02a6b5;
  }
  .picpanel {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    &::before {
      position: absolute;
      bottom: 0;
      left: 0;
      content: '';
      width: 10px;
      height: 10px;
      border-bottom: 2px solid #02a6b5;
      border-left: 2px solid #02a6b5;
    }
    &::after {
      position: absolute;
      bottom: 0;
      right: 0;
      content: '';
      width: 10px;
      height: 10px;
      border-bottom: 2px solid #02a6b5;
      border-right: 2px solid #02a6b5;
    }
  }
}
</style>