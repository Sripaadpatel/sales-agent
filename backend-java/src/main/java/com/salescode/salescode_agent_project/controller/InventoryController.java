package com.salescode.salescode_agent_project.controller;

import com.salescode.salescode_agent_project.model.Product;
import com.salescode.salescode_agent_project.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class InventoryController {

    @Autowired
    private ProductRepository repository;

    // Tool 1 for AI: Search
    @GetMapping("/products")
    public List<Product> searchProducts(@RequestParam String query) {
        return repository.findByNameContainingIgnoreCase(query);
    }

    // Tool 2 for AI: Place Order
    @PostMapping("/order")
    public String placeOrder(@RequestParam String productId, @RequestParam int quantity) {
        Product product = repository.findById(productId).orElse(null);

        if (product == null) {
            return "Error: Product not found.";
        }

        if (product.getStock() < quantity) {
            return "Error: Insufficient stock. Only " + product.getStock() + " available.";
        }

        product.setStock(product.getStock() - quantity);
        repository.save(product);

        return "Success: Ordered " + quantity + " of " + product.getName() + ". Remaining Stock: " + product.getStock();
    }
}