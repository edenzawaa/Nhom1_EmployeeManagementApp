package controllers;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import models.Employee;

public class EmployeeController {

    @FXML
    private TableView<Employee> employeeTable;

    @FXML
    private TableColumn<Employee, String> colId;

    @FXML
    private TableColumn<Employee, String> colName;

    @FXML
    private TableColumn<Employee, String> colDepartment;

    @FXML
    private TableColumn<Employee, String> colPosition;

    @FXML
    private TableColumn<Employee, Double> colSalary;

    @FXML
    private TextField txtId;

    @FXML
    private TextField txtName;

    @FXML
    private TextField txtDepartment;

    @FXML
    private TextField txtPosition;

    @FXML
    private TextField txtSalary;

    @FXML
    private Button btnAdd;

    @FXML
    private Button btnUpdate;

    @FXML
    private Button btnDelete;

    @FXML
    private Button btnClear;

    // Danh sách nhân viên hiển thị trên bảng
    private final ObservableList<Employee> employeeList = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        // Ánh xạ cột với thuộc tính trong lớp Employee
        colId.setCellValueFactory(new PropertyValueFactory<>("id"));
        colName.setCellValueFactory(new PropertyValueFactory<>("name"));
        colDepartment.setCellValueFactory(new PropertyValueFactory<>("department"));
        colPosition.setCellValueFactory(new PropertyValueFactory<>("position"));
        colSalary.setCellValueFactory(new PropertyValueFactory<>("salary"));

        // Dữ liệu mẫu ban đầu
        employeeList.addAll(
            new Employee("E001", "Nguyen Van A", "IT", "Developer", 12000000),
            new Employee("E002", "Tran Thi B", "HR", "HR Manager", 15000000)
        );

        // Gắn dữ liệu lên bảng
        employeeTable.setItems(employeeList);

        // Khi chọn dòng → hiển thị thông tin lên form
        employeeTable.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                txtId.setText(newVal.getId());
                txtName.setText(newVal.getName());
                txtDepartment.setText(newVal.getDepartment());
                txtPosition.setText(newVal.getPosition());
                txtSalary.setText(String.valueOf(newVal.getSalary()));
            }
        });
    }

    // Thêm nhân viên 
    @FXML
    private void addEmployee() {
        String id = txtId.getText();
        String name = txtName.getText();
        String dept = txtDepartment.getText();
        String pos = txtPosition.getText();
        String salaryText = txtSalary.getText();

        if (id.isEmpty() || name.isEmpty() || dept.isEmpty() || pos.isEmpty() || salaryText.isEmpty()) {
            showAlert(" Vui lòng nhập đầy đủ thông tin!");
            return;
        }

        try {
            double salary = Double.parseDouble(salaryText);
            Employee newEmp = new Employee(id, name, dept, pos, salary);
            employeeList.add(newEmp);
            clearForm();
        } catch (NumberFormatException e) {
            showAlert(" Lương phải là số!");
        }
    }

    // Cập nhật thông tin
    @FXML
    private void updateEmployee() {
        Employee selected = employeeTable.getSelectionModel().getSelectedItem();

        if (selected == null) {
            showAlert(" Vui lòng chọn nhân viên cần sửa!");
            return;
        }

        try {
            selected.setId(txtId.getText());
            selected.setName(txtName.getText());
            selected.setDepartment(txtDepartment.getText());
            selected.setPosition(txtPosition.getText());
            selected.setSalary(Double.parseDouble(txtSalary.getText()));

            employeeTable.refresh();
            clearForm();
        } catch (NumberFormatException e) {
            showAlert(" Lương phải là số!");
        }
    }

    // Xóa nhân viên 
    @FXML
    private void deleteEmployee() {
        Employee selected = employeeTable.getSelectionModel().getSelectedItem();
        if (selected != null) {
            employeeList.remove(selected);
            clearForm();
        } else {
            showAlert(" Hãy chọn nhân viên cần xoá!");
        }
    }

    // Dọn form 
    @FXML
    private void clearForm() {
        txtId.clear();
        txtName.clear();
        txtDepartment.clear();
        txtPosition.clear();
        txtSalary.clear();
        employeeTable.getSelectionModel().clearSelection();
    }

    // Hiển thị cảnh báo 
    private void showAlert(String msg) {
        Alert alert = new Alert(Alert.AlertType.WARNING);
        alert.setTitle("Thông báo");
        alert.setHeaderText(null);
        alert.setContentText(msg);
        alert.showAndWait();
    }
}
