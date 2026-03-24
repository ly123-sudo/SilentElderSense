<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="title">异常行为识别与应急响应系统</h1>
        <p class="subtitle">面向独居老人的隐私保护型智能监测平台</p>
      </div>

      <el-form ref="formRef" :model="formData" :rules="formRules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-form-item v-if="isRegisterMode" prop="email">
          <el-input
            v-model="formData.email"
            placeholder="请输入邮箱"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ isRegisterMode ? '注册' : '登录' }}
          </el-button>
        </el-form-item>

        <div class="switch-mode">
          <el-button type="text" @click="toggleMode">
            {{ isRegisterMode ? '已有账号？去登录' : '没有账号？去注册' }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login, register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const isRegisterMode = ref(false)

const formData = reactive({
  username: '',
  password: '',
  email: ''
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isRegisterMode.value) {
          // 注册
          await register({
            username: formData.username,
            password: formData.password,
            email: formData.email
          })
          ElMessage.success('注册成功，请登录')
          isRegisterMode.value = false
        } else {
          // 登录
          await authStore.login({
            username: formData.username,
            password: formData.password
          })
          ElMessage.success('登录成功')
          router.push('/dashboard')
        }
      } catch (error) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 450px;
  padding: 50px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-top: 30px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  margin-top: 20px;
}

.login-button:hover {
  opacity: 0.9;
}

.switch-mode {
  text-align: center;
  margin-top: 15px;
}
</style>
