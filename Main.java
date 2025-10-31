package main;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import javafx.scene.Parent;

public class Main extends Application {

    @Override
    public void start(Stage primaryStage) {
        try {
            // Nạp file giao diện chính (Dashboard)
            Parent root = FXMLLoader.load(getClass().getResource("/views/dashboard.fxml"));

            // Tạo Scene với kích thước ban đầu
            Scene scene = new Scene(root, 1100, 700);

            // Thêm file CSS
            scene.getStylesheets().add(getClass().getResource("/css/style.css").toExternalForm());

            // Cấu hình Stage (cửa sổ chính)
            primaryStage.setTitle("Employee Attendance & Performance Management System");
            primaryStage.setResizable(true);  // cho phép phóng to / thu nhỏ cửa sổ
            primaryStage.getIcons().add(new Image(getClass().getResourceAsStream("/images/app_icon.png"))); // icon tuỳ chọn

            // Gắn Scene vào Stage
            primaryStage.setScene(scene);

            // Hiển thị cửa sổ
            primaryStage.show();

        } catch (Exception e) {
            e.printStackTrace();
            System.out.println(" Lỗi khi khởi chạy ứng dụng: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
