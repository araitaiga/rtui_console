"""
ROS2 client and log generation utilities
"""
from datetime import datetime
import os
import queue
import random
import threading
from typing import Callable, Optional

from .models import LogLevel
from .models import LogMessage

# Check ROS2 availability
try:
    from rcl_interfaces.msg import Log
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import DurabilityPolicy
    from rclpy.qos import HistoryPolicy
    from rclpy.qos import QoSProfile
    from rclpy.qos import ReliabilityPolicy
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    Log = None
    Node = None


# Define ROS2LogSubscriber based on availability
if ROS2_AVAILABLE and Node:
    class ROS2LogSubscriber(Node):
        """ROS2 node that subscribes to rosout topic"""

        def __init__(self, log_queue: queue.Queue, status_callback: Optional[Callable] = None):
            super().__init__('rtui_console_subscriber')
            self.log_queue = log_queue
            self.status_callback = status_callback
            self.message_count = 0
            self.last_message_time = None

            # QoS profile for rosout topic
            qos_profile = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=1000,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE
            )

            try:
                self.subscription = self.create_subscription(
                    Log,
                    '/rosout',
                    self.log_callback,
                    qos_profile
                )
                self.get_logger().info("Successfully subscribed to /rosout")
                if self.status_callback:
                    self.status_callback("Connected to /rosout")
            except Exception as e:
                self.get_logger().error(f"Failed to subscribe to /rosout: {e}")
                if self.status_callback:
                    self.status_callback(f"Failed to subscribe: {e}")

        def log_callback(self, msg):
            """Callback for receiving log messages"""
            try:
                log_msg = LogMessage(msg)
                self.log_queue.put(log_msg, block=False)
                self.message_count += 1
                self.last_message_time = datetime.now()

                # Periodic status updates
                if self.message_count % 10 == 0 and self.status_callback:
                    self.status_callback(
                        f"Received {self.message_count} messages")

            except queue.Full:
                # Queue is full, drop oldest messages
                try:
                    self.log_queue.get_nowait()
                    self.log_queue.put(log_msg, block=False)
                except queue.Empty:
                    pass
            except Exception as e:
                self.get_logger().error(f"Error in log callback: {e}")

else:
    class ROS2LogSubscriber:
        """Dummy ROS2 subscriber for when ROS2 is not available"""

        def __init__(self, log_queue: queue.Queue, status_callback: Optional[Callable] = None):
            raise ImportError("ROS2 packages not available")

        def destroy_node(self):
            pass


class ROS2Client:
    """ROS2 client manager"""

    def __init__(self, log_queue: queue.Queue):
        self.log_queue = log_queue
        self.node: Optional[ROS2LogSubscriber] = None
        self.thread: Optional[threading.Thread] = None
        self.status = "Disconnected"

    def is_available(self) -> bool:
        """Check if ROS2 is available"""
        return ROS2_AVAILABLE

    def check_environment(self) -> tuple[bool, str]:
        """Check ROS2 environment setup"""
        if not ROS2_AVAILABLE:
            return False, "ROS2 packages not installed"

        ros_distro = os.getenv('ROS_DISTRO')
        if not ros_distro:
            return False, "ROS2 environment not detected. Please source setup.bash first!"

        return True, f"ROS2 {ros_distro} environment detected"

    def start_subscriber(self) -> bool:
        """Start ROS2 subscriber in a separate thread"""
        if not ROS2_AVAILABLE:
            return False

        def ros_thread_func():
            try:
                rclpy.init()
                self.node = ROS2LogSubscriber(self.log_queue)
                self.status = "Connected"
                rclpy.spin(self.node)
            except Exception as e:
                self.status = f"Error: {e}"
            finally:
                if self.node:
                    self.node.destroy_node()
                try:
                    rclpy.shutdown()
                except:
                    pass
                self.status = "Disconnected"

        self.thread = threading.Thread(target=ros_thread_func, daemon=True)
        self.thread.start()
        return True

    def stop_subscriber(self):
        """Stop ROS2 subscriber"""
        if self.node:
            self.node.destroy_node()
        self.status = "Disconnected"

    def get_status(self) -> str:
        """Get current connection status"""
        return self.status


class LogGenerator:
    """Test log generator utility"""

    TEST_NODES = [
        "test_node", "publisher_node", "subscriber_node",
        "navigation_node", "sensor_driver", "camera_node",
        "lidar_driver", "planning_node", "control_node"
    ]

    TEST_MESSAGES = [
        "Starting node initialization",
        "Published message to topic /test",
        "Received callback from /sensor_data",
        "Processing complete",
        "Warning: Low battery detected",
        "Error: Failed to connect to service",
        "Debug: Variable x = 42",
        "Camera sensor connected",
        "Navigation system ready",
        "Emergency stop activated",
        "Sensor calibration complete",
        "Path planning in progress",
        "Target reached successfully",
        "System health check passed"
    ]

    @classmethod
    def generate_test_logs(cls, log_queue: queue.Queue, count: int = 20):
        """Generate test log messages"""
        levels = [LogLevel.DEBUG, LogLevel.INFO,
                  LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL]

        for i in range(count):
            node = random.choice(cls.TEST_NODES)
            message = random.choice(cls.TEST_MESSAGES)
            level = random.choice(levels)

            log_msg = LogMessage(
                timestamp=datetime.now(),
                level=level,
                name=node,
                text=f"{message} #{i+1}",
                file="test.py",
                function="test_function",
                line=42 + i
            )

            try:
                log_queue.put(log_msg, block=False)
            except queue.Full:
                break

        return count
