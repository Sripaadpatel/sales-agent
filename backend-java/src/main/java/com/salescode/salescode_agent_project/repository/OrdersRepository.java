package com.salescode.salescode_agent_project.repository;

import com.salescode.salescode_agent_project.model.Orders;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface OrdersRepository extends JpaRepository<Orders, String> {
    @Query("SELECT o FROM Orders o WHERE o.status = 'CONFIRMED' ORDER BY o.order_date DESC LIMIT 5")
    public List<Orders> FiveRecentOrders();
}
