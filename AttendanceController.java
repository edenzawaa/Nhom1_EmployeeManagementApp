package controllers;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;

import java.time.LocalDate;

public class AttendanceController {

    @FXML
    private TableView<AttendanceRecord> attendanceTable;

    @FXML
    private TableColumn<AttendanceRecord, String> colEmployeeId;

    @FXML
    private TableColumn<AttendanceRecord, String> colEmployeeName;

    @FXML
    private TableColumn<AttendanceRecord, LocalDate> colDate;

    @FXML
    private TableColumn<AttendanceRecord, String> colStatus;

    @FXML
    private TextField txtEmployeeId;

    @FXML
    private TextField txtEmployeeName;

    @FXML
    private DatePicker dpDate;

    @FXML
    private ComboBox<String> cbStatus;

    @FXML
    private Button btnAdd;

    @FXML
    private Button btnDelete;

    // Danh sách lưu trữ tạm dữ liệu điểm danh
    private final ObservableList<AttendanceRecord> attendanceList = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        // Cấu hình cột bảng
        colEmployeeId.setCellValueFactory(new PropertyValueFactory<>("employeeId"));
        colEmployeeName.setCellValueFactory(new PropertyValueFactory<>("employeeName"));
        colDate.setCellValueFactory(new PropertyValueFactory<>("date"));
        colStatus.setCellValueFactory(new PropertyValueFactory<>("status"));

        // Cấu hình combo box trạng thái
        cbStatus.setItems(FXCollections.observableArrayList("Present", "Absent", "Late", "On Leave"));

        // Gán dữ liệu mẫu ban đầu
        attendanceList.addAll(
                new AttendanceRecord("E001", "Nguyen Van A", LocalDate.now(), "Present"),
                new AttendanceRecord("E002", "Tran Thi B", LocalDate.now(), "Absent")
        );

        attendanceTable.setItems(attendanceList);
    }

    // Thêm bản ghi điểm danh
    @FXML
    private void addAttendance() {
        String id = txtEmployeeId.getText();
        String name = txtEmployeeName.getText();
        LocalDate date = dpDate.getValue();
        String status = cbStatus.getValue();

        if (id.isEmpty() || name.isEmpty() || date == null || status == null) {
            showAlert(" Vui lòng nhập đầy đủ thông tin trước khi thêm!");
            return;
        }

        AttendanceRecord record = new AttendanceRecord(id, name, date, status);
        attendanceList.add(record);

        clearForm();
    }

    // Xoá bản ghi được chọn
    @FXML
    private void deleteAttendance() {
        AttendanceRecord selected = attendanceTable.getSelectionModel().getSelectedItem();
        if (selected != null) {
            attendanceList.remove(selected);
        } else {
            showAlert(" Vui lòng chọn một bản ghi để xoá!");
        }
    }

    // Dọn form sau khi thêm =
    private void clearForm() {
        txtEmployeeId.clear();
        txtEmployeeName.clear();
        dpDate.setValue(null);
        cbStatus.setValue(null);
    }

    // Hiển thị thông báo cảnh báo
    private void showAlert(String message) {
        Alert alert = new Alert(Alert.AlertType.WARNING);
        alert.setTitle("Thông báo");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    // Lớp con dùng để lưu trữ dữ liệu bảng 
    public static class AttendanceRecord {
        private final String employeeId;
        private final String employeeName;
        private final LocalDate date;
        private final String status;

        public AttendanceRecord(String employeeId, String employeeName, LocalDate date, String status) {
            this.employeeId = employeeId;
            this.employeeName = employeeName;
            this.date = date;
            this.status = status;
        }

        public String getEmployeeId() {
            return employeeId;
        }

        public String getEmployeeName() {
            return employeeName;
        }

        public LocalDate getDate() {
            return date;
        }

        public String getStatus() {
            return status;
        }
    }
}
