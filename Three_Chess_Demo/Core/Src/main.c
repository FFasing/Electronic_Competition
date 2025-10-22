/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "i2c.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "string.h"
#include "oled.h"
#include "math.h"
#include "stdio.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
typedef struct{
	double angel;
	int count;
}SERVO;
SERVO servo1,servo2;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void FF_Motor_Init(void){
	HAL_TIM_PWM_Start(&htim1,TIM_CHANNEL_1);
	TIM1->ARR=1000-1;
	TIM1->PSC=800-1;
	HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_2);
	TIM2->ARR=1000-1;
	TIM2->PSC=800-1;
}
//motor is motor's selsetion 0 or 1
//direction is motor's direction 0-3 ,0 is stop
//speed is motor's speed 0-100
void FF_Motor_Control(uint8_t motor,uint8_t direction,uint8_t speed){
	if(motor==0)
	{
		if(direction==0)
		{
		  HAL_GPIO_WritePin(GPIOA,GPIO_PIN_0,0);
		  __HAL_TIM_SetCompare(&htim1,TIM_CHANNEL_1,0);
		  HAL_GPIO_WritePin(GPIOC,GPIO_PIN_1,0);
		  __HAL_TIM_SetCompare(&htim2,TIM_CHANNEL_2,0);
		}
		if(direction==1)
		{
		  HAL_GPIO_WritePin(GPIOA,GPIO_PIN_0,0);
		  __HAL_TIM_SetCompare(&htim1,TIM_CHANNEL_1,0);
		  HAL_GPIO_WritePin(GPIOC,GPIO_PIN_1,1);
		  __HAL_TIM_SetCompare(&htim2,TIM_CHANNEL_2,speed*10);
		}
		if(direction==2)
		{
		  HAL_GPIO_WritePin(GPIOC,GPIO_PIN_1,0);
		  __HAL_TIM_SetCompare(&htim2,TIM_CHANNEL_2,0);
		  HAL_GPIO_WritePin(GPIOA,GPIO_PIN_0,1);
		  __HAL_TIM_SetCompare(&htim1,TIM_CHANNEL_1,speed*10);
		}
	}
}
void FF_Servo_Init(SERVO *servo, const int count) {
	HAL_TIM_PWM_Start(&SERVO1,TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&SERVO2,TIM_CHANNEL_1);
	servo->count = count;

	if (servo == &servo1) {
		TIM2->PSC = 800 - 1;      // SERVO1 80 000 000
		TIM2->ARR = servo1.count - 1;
	}
	else if (servo == &servo2) {
		TIM3->PSC = 800 - 1;      // SERVO2
		TIM3->ARR = servo2.count - 1;
	}
}
void FF_Servo_move_angle(const SERVO *servo, double angle) {
	if (angle < 0) angle = 0;
	if (angle > 180) angle = 180;
	const float num = servo->count;
	const float pwm_min = num * 0.05;
	const float pwm_max = num * 0.25;
	const int pwm_num = (int)(pwm_min + (pwm_max - pwm_min) * (angle / 180.0));
	if (servo == &servo1) {
		__HAL_TIM_SET_COMPARE(&SERVO1, TIM_CHANNEL_2, pwm_num);  // SERVO1
	}
	else if (servo == &servo2) {
		__HAL_TIM_SET_COMPARE(&SERVO2, TIM_CHANNEL_1, pwm_num);  // SERVO2
	}
}
void FF_Servo_move_cord(const SERVO *Ser1,const SERVO *Ser2, double x,double y ){
	const double arm_length1 = 87.3, arm_length2 = 87.3;
	const double distance_sq = x * x + y * y;
	const double distance = sqrt(distance_sq);
	double angle_arm1_rad=0;
	double angle_arm2_rad=0;
	char max = 0;
	// 检查是否在可达范围内
	if (distance > arm_length1 + arm_length2 || distance < fabs(arm_length1 - arm_length2)) {
		double angle_arm1_deg=0;
		max=1;
		angle_arm2_rad=0;
		angle_arm1_rad=atan2(y, x);
		// 最终角度（转换为度数）
		if (x<0)	angle_arm1_deg = (angle_arm1_rad) * 180.0 / M_PI;
		double angle_arm2_deg = angle_arm2_rad;
		// 控制舵机
		FF_Servo_move_angle(Ser1, angle_arm1_deg-30);
		FF_Servo_move_angle(Ser2, angle_arm2_deg+45);
	}
	if (max == 0) {
		// 计算第一个舵机角度（相对于X轴）
		double angle_origin_to_x = atan2(y, x);  // 使用 atan2 自动处理 y < 0 的情况
		// 使用余弦定理计算第二个舵机角度
		double cos_angle_arm2 = (distance_sq - arm_length1 * arm_length1 - arm_length2 * arm_length2) / (2 * arm_length1 * arm_length2);
		angle_arm2_rad = acos(cos_angle_arm2);
		// 计算第一个舵机角度（相对于基座）
		double cos_angle_arm1 = (arm_length1 * arm_length1 + distance_sq - arm_length2 * arm_length2) / (2 * arm_length1 * distance);
		angle_arm1_rad = acos(cos_angle_arm1);
		// 最终角度（转换为度数）
		double angle_arm1_deg = (angle_origin_to_x + angle_arm1_rad) * 180.0 / M_PI;
		double angle_arm2_deg = angle_arm2_rad * 180.0 / M_PI;
		// 控制舵机
		FF_Servo_move_angle(Ser1, angle_arm1_deg-30);
		FF_Servo_move_angle(Ser2, angle_arm2_deg+45);
	}
}
void FF_OLED_Init(void) {
	HAL_Delay(20);
	OLED_Init();
	OLED_NewFrame();
	OLED_PrintASCIIString(0,0,"Huang Fan",&afont8x6,OLED_COLOR_NORMAL);
	OLED_DrawCircle(100,45,18,OLED_COLOR_NORMAL);
	OLED_DrawFilledCircle(93,43,3,OLED_COLOR_NORMAL);
	OLED_DrawFilledCircle(107,43,3,OLED_COLOR_NORMAL);
	OLED_DrawLine(95,55,105,52,OLED_COLOR_NORMAL);
	OLED_DrawLine(95,52,105,55,OLED_COLOR_NORMAL);
	OLED_DrawLine(96,55,106,52,OLED_COLOR_NORMAL);
	OLED_DrawLine(96,52,106,55,OLED_COLOR_NORMAL);
	OLED_ShowFrame();
}
//This is competition of 2024
int l_test = 9;
void FF_Servo_move_to_lattice(int lattice) {	//移动到格子
	const int lattice_x[9] = {-38, -10, 27, -38, -5, 27, -38, -10, 27};
	const int lattice_y[9] = {120, 120, 120, 95, 95, 95, 65, 70, 70};
  	FF_Servo_move_cord(&servo1,&servo2,lattice_x[lattice-1],lattice_y[lattice-1]) ;
}
void FF_Servo_move_to_chess(char color, int chess) {	//移动到棋子 color=0-black 1-white
	const int black_chess_x[5] = {-85, -80, -80, -80, -80};
	const int black_chess_y[5] = {45, 70, 91, 115, 140};
	if (color==0) FF_Servo_move_cord(&servo1,&servo2,black_chess_x[chess],black_chess_y[chess]) ;
}
void FF_Servo_move_to_init(void) {
	FF_Servo_move_angle(&servo1,180);
	FF_Servo_move_angle(&servo2,130);
	HAL_Delay(500);
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_I2C1_Init();
  MX_TIM4_Init();
  MX_TIM17_Init();
  MX_TIM2_Init();
  MX_TIM1_Init();
  MX_TIM3_Init();
  /* USER CODE BEGIN 2 */
	FF_Servo_Init(&servo1,1000);
	FF_Servo_Init(&servo2,1000);
	FF_OLED_Init();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	int test_num=0;
  	FF_Servo_move_to_init();
  while (1){
  	//FF_Servo_move_to_lattice(5);
  	//FF_Servo_move_to_lattice(l_test);
  	//if (test_num>=10) test_num=1;
  	//FF_Servo_move_cord(&servo1, &servo2, -85, 45);
  	//FF_Servo_move_to_chess(0,test_num++);
  	//if (test_num>=5) test_num=0;
  	//FF_Servo_move_angle(&servo1, 180-30);
  	HAL_Delay(1000);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = RCC_PLLM_DIV2;
  RCC_OscInitStruct.PLL.PLLN = 10;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
