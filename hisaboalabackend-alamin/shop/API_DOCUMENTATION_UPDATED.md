# Shop Management API Documentation

## Overview
This API provides comprehensive endpoints for managing shops, products, categories, units, transactions, and pricing in a dynamic e-commerce system.

## Base URL
All endpoints are relative to your Django application's base URL.

## Authentication
All endpoints require authentication. Include authentication headers with your requests.

## Understanding the System

### Product Quantity System
This system uses a dynamic approach to quantity tracking:

**For Egg Products:**
- `quantity`: Number of pieces (eggs)
- `pieces_count`: Not used (should be null)
- Example: 100 eggs = `{"quantity": 100.0, "pieces_count": null}`

**For Hen/Chicken Products:**
- `quantity`: Weight in kilograms (for calculations and base stock)
- `pieces_count`: Number of individual chickens (for piece tracking)
- Example: 15 chickens weighing 90kg = `{"quantity": 90.0, "pieces_count": 15}`

**Hen Stock Tracking:**
- `current_stock`: Total weight in kg (used for price calculations)
- `pieces_count`: Total number of chickens (for counting individual birds)
- Both fields are automatically updated during buy/sell transactions

### Unit-Based Pricing
Each product can have multiple selling prices for different units:
- **Eggs**: Per piece (₹12), Per dozen (₹140), Per tray-30 (₹350)
- **Chicken**: Per kg (₹150), Per piece (₹200)

When adding a product, include a `prices` array to set unit-specific prices:
```json
"prices": [
    {"unit_id": 1, "price": "12.00"},    // Per piece
    {"unit_id": 2, "price": "140.00"}    // Per dozen
]
```

### Business Rules
1. **Stock Tracking**: Always based on `quantity` field
2. **Dual Tracking**: For hen/chicken, optionally track both weight (quantity) and count (pieces_count)
3. **Price Updates**: Can update base price or unit-specific prices
4. **Transactions**: All purchases/sales create transaction records

---

## 1. Add Product to Shop (Buy New Product)

**Endpoint:** `POST /api/shop-products/add_product/`

**Description:** Add a new product to shop with purchase transaction details. This endpoint creates both the product and the purchase transaction.

**Required Fields:**
- `shop_id`: Shop ID
- `subcategory`: Product subcategory ID
- `quantity`: Quantity being purchased (required)
- `buying_price_per_unit`: Price per unit for purchase (required)
- `payment_method`: Payment method (required)

**Request Format:**
```json
{
    "shop_id": 1,
    "subcategory": 2,
    "initial_stock": 0,
    "quantity": 50,
    "buying_price_per_unit": 25.50,
    "payment_method": "CASH",
    "due_amount": 0,
    "due_date": null,
    "supplier_id": 3,
    "external_party_name": "",
    "notes": "Fresh stock purchase",
    "pieces_count": null,
    "prices": [
        {
            "unit_id": 1,
            "price": "30.00"
        },
        {
            "unit_id": "2",
            "unit_id": 2,
            "price": "25.00"
        }
    ]
}
```

**For Hen/Chicken Products (Weight-based):**
```json
{
    "shop_id": 1,
    "subcategory": 3,
    "quantity": 90.0,
    "buying_price_per_unit": 120.0,
    "payment_method": "CASH",
    "pieces_count": 15,
    "notes": "Bought 15 chickens weighing 90kg total",
    "prices": [
        {
            "unit_id": 4,
            "price": "150.00"
        },
        {
            "unit_id": 5,
            "price": "140.00"
        }
    ]
}
```

**For Egg Products (Count-based):**
```json
{
    "shop_id": 1,
    "subcategory": 2,
    "quantity": 100.0,
    "buying_price_per_unit": 10.0,
    "payment_method": "CASH",
    "notes": "Bought 100 eggs",
    "prices": [
        {
            "unit_id": 1,
            "price": "12.00"
        },
        {
            "unit_id": 2,
            "price": "140.00"
        }
    ]
}
```

**Important Notes for Prices Array:**
- `unit_id` must be an integer (not string)
- `price` should be a decimal string
- Each unit_id must exist in the database
- Units must be allowed for the product's category

**Payment Method Options:**
- `CASH`: Cash payment
- `BANK`: Bank transfer
- `MOBILE`: Mobile banking
- `DUE`: Due payment

**For Due Payments:**
```json
{
    "shop_id": 1,
    "subcategory": 2,
    "quantity": 100,
    "buying_price_per_unit": 20.00,
    "payment_method": "DUE",
    "due_amount": 2000.00,
    "due_date": "2025-08-15",
    "supplier_id": 3,
    "notes": "Bulk purchase on credit"
}
```

**For Partial Payment:**
```json
{
    "shop_id": 1,
    "subcategory": 2,
    "quantity": 50,
    "buying_price_per_unit": 30.00,
    "payment_method": "CASH",
    "due_amount": 500.00,
    "due_date": "2025-08-10",
    "supplier_id": 3,
    "notes": "Paid 1000, remaining 500 due"
}
```

**Response:**
```json
{
    "id": 1,
    "shop": {
        "id": 1,
        "name": "Main Shop"
    },
    "subcategory": {
        "id": 2,
        "name": "Brown Eggs",
        "category": {
            "id": 1,
            "name": "Eggs"
        }
    },
    "current_stock": "50.000",
    "pieces_count": null,
    "base_unit_symbol": "pcs",
    "stock_display": "50.000 pcs",
    "prices": [
        {
            "id": 23,
            "unit": {
                "id": 1,
                "name": "Per Piece",
                "symbol": "pc"
            },
            "price": "30.00"
        },
        {
            "id": 24,
            "unit": {
                "id": 2,
                "name": "Per Dozen",
                "symbol": "dz"
            },
            "price": "25.00"
        }
    ],
    "transaction_created": true,
    "product_created": true,
    "quantity_purchased": 50,
    "buying_price_per_unit": "25.50",
    "payment_method": "CASH",
    "total_amount": 1275.00,
    "due_amount": 0,
    "is_paid": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. Sell Product (Create Sale Transaction)

**Endpoint 1:** `POST /api/shop-products/{product_id}/sell_product/`
**Endpoint 2:** `POST /api/shop-products/sell/` (General selling endpoint)

**Description:** Sell products from your shop stock and create sale transactions. This endpoint automatically updates stock and tracks payment status.

**Required Fields:**
- `product_id`: Product ID to sell (for general endpoint)
- `quantity`: Quantity to sell (required)
- `unit_id`: Unit for the sale (required)
- `selling_price_per_unit`: Selling price per unit (required)
- `payment_method`: Payment method (required) - CASH, BANK, MOBILE, or DUE

**Basic Sale Request:**
```json
{
    "product_id": 1,
    "quantity": 10,
    "unit_id": 1,
    "selling_price_per_unit": 35.00,
    "payment_method": "CASH",
    "customer_name": "John Doe",
    "notes": "Regular customer sale"
}
```

**Sale with Partial Payment:**
```json
{
    "product_id": 1,
    "quantity": 20,
    "unit_id": 1,
    "selling_price_per_unit": 35.00,
    "payment_method": "CASH",
    "due_amount": 200.00,
    "due_date": "2025-08-20",
    "customer_name": "Jane Smith",
    "notes": "Paid 500, remaining 200 due"
}
```

**Sale on Credit (Full Due):**
```json
{
    "product_id": 1,
    "quantity": 30,
    "unit_id": 1,
    "selling_price_per_unit": 35.00,
    "payment_method": "DUE",
    "due_amount": 1050.00,
    "due_date": "2025-08-25",
    "customer_name": "ABC Restaurant",
    "notes": "Monthly credit sale"
}
```

**Sale with Pieces Count (for hen/chicken):**
```json
{
    "product_id": 2,
    "quantity": 5,
    "unit_id": 3,
    "selling_price_per_unit": 180.00,
    "payment_method": "CASH",
    "pieces_count": 5,
    "customer_name": "XYZ Traders",
    "notes": "Live chicken sale"
}
```

**Response:**
```json
{
    "id": 1,
    "shop": 1,
    "subcategory": 2,
    "subcategory_name": "Brown Eggs",
    "category_name": "Eggs",
    "current_stock": "40.000",
    "base_unit_symbol": "pcs",
    "stock_display": "40.000 pcs",
    "transaction_created": true,
    "transaction_id": 5,
    "quantity_sold": 10,
    "selling_price_per_unit": "35.00",
    "total_amount": 350.00,
    "due_amount": 0,
    "is_paid": true,
    "customer_name": "John Doe",
    "payment_method": "CASH"
}
```

**Stock Validation:**
The system automatically checks if sufficient stock is available before allowing the sale. If insufficient stock, you'll get an error like:
```json
{
    "non_field_errors": ["Insufficient stock. Available: 5.000 pcs, Requested: 10.000 pcs"]
}
```

---

## 3. Update Stock (Manual)

**Endpoint:** `POST /api/shop-products/{product_id}/update_stock/`

**Description:** Manually update product stock without creating any transaction. This is for direct stock adjustments only. Buying and selling products automatically handle stock updates through transactions.

**Request Format:**
```json
{
    "current_stock": 75.0,
    "pieces_count": 12,
    "notes": "Manual adjustment after inventory count"
}
```

**For Egg Products:**
```json
{
    "current_stock": 150.0,
    "notes": "Corrected stock after physical count"
}
```

**For Hen Products:**
```json
{
    "current_stock": 45.5,
    "pieces_count": 8,
    "notes": "Updated after inventory"
}
```

**Required Fields:**
- `current_stock`: New stock quantity (required)

**Optional Fields:**
- `pieces_count`: Number of pieces for tracking (optional, used for hen products)
- `notes`: Notes for the stock update (optional)

**Response:**
```json
{
    "id": 1,
    "shop": 1,
    "subcategory": 2,
    "subcategory_name": "Deshi Murgi",
    "category_name": "Murgi",
    "current_stock": "45.50",
    "pieces_count": 8,
    "manual_update": true,
    "old_stock": "50.00",
    "new_stock": "45.50",
    "old_pieces_count": 10,
    "new_pieces_count": 8,
    "notes": "Updated after inventory",
    "stock_updated": true
}
```

**Note:** This endpoint is only for manual stock corrections. Stock updates for buying and selling products happen automatically when you use the `add_product` and `sell_product` endpoints.

### Tracking Hen Stock in Pieces

For hen/chicken products, you can track both the total weight (in kg) and the number of individual chickens:

**Key Fields:**
- `current_stock`: Total weight in kilograms (used for price calculations)
- `pieces_count`: Number of individual chickens (for counting birds)

**Example Scenarios:**

1. **Adding 10 chickens weighing 60kg:**
   ```json
   {
     "quantity": 60.0,
     "pieces_count": 10
   }
   ```

2. **Current stock check:**
   ```json
   {
     "current_stock": "150.50",  // Total weight: 150.5 kg
     "pieces_count": 25          // Total chickens: 25 birds
   }
   ```

3. **Selling 3 chickens weighing 18kg:**
   ```json
   {
     "quantity": 18.0,
     "pieces_count": 3
   }
   ```

**Important Notes:**
- Both `current_stock` and `pieces_count` are automatically updated during buy/sell transactions
- For manual stock updates, you can update both fields independently
- Price calculations always use the weight (`current_stock`) not the piece count
- The piece count is purely for inventory tracking purposes

---

## 4. Update Product Base Price

**Endpoint:** `POST /api/shop-products/{product_id}/update_base_price/`

**Description:** Update the base selling price of a product (price for base unit)

**Request Format:**
```json
{
    "base_price": 35.00
}
```

**Response:**
```json
{
    "id": 1,
    "shop": 1,
    "subcategory": 2,
    "subcategory_name": "Brown Eggs",
    "category_name": "Eggs",
    "current_stock": "50.000",
    "base_unit_symbol": "pcs",
    "base_price": "35.00",
    "base_price_updated": true,
    "price_created": false
}
```

---

## 5. Update Unit-Specific Price

**Endpoint:** `POST /api/product-prices/update_unit_price/`

**Description:** Update selling price for a specific product and unit combination

**Request Format:**
```json
{
    "product_id": 1,
    "unit_id": 2,
    "price": 28.50
}
```

**Response:**
```json
{
    "id": 5,
    "unit": 2,
    "unit_name": "Dozen",
    "unit_symbol": "dzn",
    "price": "28.50",
    "updated": true,
    "created": false
}
```

---

## 5. Shop Management

### List User's Shops
**Endpoint:** `GET /api/shops/`

### Create New Shop
**Endpoint:** `POST /api/shops/`
```json
{
    "name": "My Poultry Shop",
    "district": "Dhaka",
    "upozila": "Dhanmondi",
    "address": "123 Main Street",
    "phone": "01700000000"
}
```

### Get Shop Details
**Endpoint:** `GET /api/shops/{shop_id}/`

### Update Shop
**Endpoint:** `PUT /api/shops/{shop_id}/`

### Delete Shop
**Endpoint:** `DELETE /api/shops/{shop_id}/`

---

## 6. Product Management

### List Products
**Endpoint:** `GET /api/shop-products/`
**Query Parameters:**
- `shop_id`: Filter by shop
- `category_id`: Filter by category
- `include_units=true`: Include allowed units for each product

**Response (for hen products with pieces tracking):**
```json
[
  {
    "id": 1,
    "shop": {
      "id": 1,
      "name": "Main Shop"
    },
    "subcategory": {
      "id": 2,
      "name": "Deshi Murgi",
      "category": {
        "id": 1,
        "name": "Murgi"
      }
    },
    "current_stock": "85.50",
    "pieces_count": 15,
    "base_unit_symbol": "kg",
    "stock_display": "85.50 kg (15 pieces)",
    "prices": [
      {
        "id": 1,
        "unit": {
          "id": 1,
          "name": "Per KG",
          "symbol": "kg"
        },
        "price": "160.00"
      }
    ]
  }
]
```

**Response (for egg products):**
```json
[
  {
    "id": 2,
    "shop": {
      "id": 1,
      "name": "Main Shop"
    },
    "subcategory": {
      "id": 3,
      "name": "Brown Eggs",
      "category": {
        "id": 2,
        "name": "Dim"
      }
    },
    "current_stock": "120.000",
    "pieces_count": null,
    "base_unit_symbol": "pcs",
    "stock_display": "120.000 pcs",
    "prices": [
      {
        "id": 2,
        "unit": {
          "id": 2,
          "name": "Per Piece",
          "symbol": "pc"
        },
        "price": "30.00"
      }
    ]
  }
]
```

### Get Product Details
**Endpoint:** `GET /api/shop-products/{product_id}/`

### Get Allowed Units for Product
**Endpoint:** `GET /api/shop-products/{product_id}/allowed_units/`

**Description:** Get all units that are allowed for this specific product based on its category.

**Response:**
```json
{
    "product_id": 1,
    "product_name": "Deshi Dim",
    "category": "Dim",
    "base_unit": {
        "id": 2,
        "name": "Pieces",
        "symbol": "pcs",
        "is_countable": true,
        "conversion_to_base": "1.00"
    },
    "allowed_units": [
        {
            "id": 2,
            "name": "Pieces",
            "symbol": "pcs",
            "is_countable": true,
            "conversion_to_base": "1.00"
        },
        {
            "id": 3,
            "name": "Hali",
            "symbol": "Hali",
            "is_countable": true,
            "conversion_to_base": "30.00"
        },
        {
            "id": 4,
            "name": "Dozen",
            "symbol": "dzn",
            "is_countable": true,
            "conversion_to_base": "12.00"
        }
    ]
}
```

### Include Units in Product List
**Endpoint:** `GET /api/shop-products/?include_units=true`

**Description:** When you add `include_units=true` to any product endpoint, the response will include the `allowed_units` field.

### Update Product
**Endpoint:** `PUT /api/shop-products/{product_id}/`

### Delete Product
**Endpoint:** `DELETE /api/shop-products/{product_id}/`

---

## 7. Price Management

### List All Prices
**Endpoint:** `GET /api/product-prices/`
**Query Parameters:**
- `product_id`: Filter by product

### Create Price
**Endpoint:** `POST /api/product-prices/`
```json
{
    "product": 1,
    "unit": 2,
    "price": 28.50
}
```

### Update Price
**Endpoint:** `PUT /api/product-prices/{price_id}/`
```json
{
    "price": 30.00
}
```

### Delete Price
**Endpoint:** `DELETE /api/product-prices/{price_id}/`

---

## 8. Transaction Management

### List Transactions
**Endpoint:** `GET /api/transactions/`
**Query Parameters:**
- `shop_id`: Filter by shop
- `transaction_type`: Filter by type (BUY/SELL)

### Get Transaction Details
**Endpoint:** `GET /api/transactions/{transaction_id}/`
**Response:**
```json
{
    "id": 1,
    "transaction_type": "BUY",
    "transaction_date": "2025-07-29T10:30:00Z",
    "payment_method": "CASH",
    "is_paid": true,
    "due_date": null,
    "notes": "Bulk purchase",
    "supplier": 1,
    "supplier_name": "ABC Suppliers",
    "external_party_name": "",
    "total_amount": "1500.00",
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "Brown Eggs",
            "unit": 1,
            "unit_symbol": "pcs",
            "quantity": "50.000",
            "price_per_unit": "30.00",
            "total_price": "1500.00",
            "pieces_count": null
        }
    ]
}
```

---

## 9. Category, Subcategory & Unit Management

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get category details
- `GET /api/categories/{id}/subcategories/` - Get subcategories for category
- `GET /api/categories/{id}/units/` - Get units for category

### Subcategories
- `GET /api/subcategories/` - List all subcategories
- `GET /api/subcategories/?category_id=1` - Filter by category
- `GET /api/subcategories/{id}/` - Get subcategory details

### Units
- `GET /api/units/` - List all units
- `GET /api/units/?category_id=1` - Filter by category
- `GET /api/units/{id}/` - Get unit details

---

## Field Descriptions

### Required Fields for Product Purchase
- **shop_id**: ID of the shop where product is being added
- **subcategory**: ID of the product subcategory
- **quantity**: Amount being purchased (decimal, required)
- **buying_price_per_unit**: Cost per unit (decimal, required)
- **payment_method**: How payment was made (required)

### Optional Fields
- **initial_stock**: Starting stock for new products (default: 0)
- **due_amount**: Amount still owed (default: 0)
- **due_date**: When payment is due (optional)
- **supplier_id**: ID of supplier (optional)
- **external_party_name**: Name if no supplier selected
- **notes**: Additional transaction notes
- **prices**: Array of selling prices for different units

### Business Logic
1. **Stock Management**: Stock is automatically updated by transaction items
2. **Payment Tracking**: System tracks paid/unpaid status based on due_amount
3. **Due Date Validation**: Due date is optional
4. **Supplier Handling**: Either supplier_id or external_party_name can be used
5. **Unit Conversion**: All quantities converted to base units for stock tracking
6. **Price Management**: Base price and unit-specific prices are managed separately

### Validation Rules
- Due amount cannot exceed total amount
- Payment method "DUE" requires due_amount > 0
- Supplier must exist if supplier_id provided
- Units must be valid for the product category

---

## Complete URL Structure

### Shop Management
```
GET    /api/shops/                          - List user's shops
POST   /api/shops/                          - Create new shop
GET    /api/shops/{id}/                     - Get shop details
PUT    /api/shops/{id}/                     - Update shop
DELETE /api/shops/{id}/                     - Delete shop
```

### Product Management
```
GET    /api/shop-products/                  - List user's products
GET    /api/shop-products/?shop_id=1        - Filter by shop
GET    /api/shop-products/?category_id=1    - Filter by category
GET    /api/shop-products/?include_units=true - Include allowed units
POST   /api/shop-products/                  - Create product
GET    /api/shop-products/{id}/             - Get product details
PUT    /api/shop-products/{id}/             - Update product
DELETE /api/shop-products/{id}/             - Delete product
GET    /api/shop-products/{id}/allowed_units/ - Get allowed units for product
POST   /api/shop-products/add_product/      - Add product with purchase
POST   /api/shop-products/sell/             - Sell product (general endpoint)
POST   /api/shop-products/{id}/sell_product/ - Sell specific product
POST   /api/shop-products/{id}/update_stock/ - Update stock
POST   /api/shop-products/{id}/update_base_price/ - Update base price
```

### Price Management
```
GET    /api/product-prices/                 - List all prices
GET    /api/product-prices/?product_id=1    - Filter by product
POST   /api/product-prices/                 - Create/update price
GET    /api/product-prices/{id}/            - Get price details
PUT    /api/product-prices/{id}/            - Update price
DELETE /api/product-prices/{id}/            - Delete price
POST   /api/product-prices/update_unit_price/ - Update specific unit price
```

### Transaction Management
```
GET    /api/transactions/                   - List user's transactions
GET    /api/transactions/?shop_id=1         - Filter by shop
GET    /api/transactions/?transaction_type=BUY - Filter by type
GET    /api/transactions/{id}/              - Get transaction details with items
```

### Category, Subcategory & Unit Management
```
GET    /api/categories/                     - List all categories
GET    /api/categories/{id}/                - Get category details
GET    /api/categories/{id}/subcategories/  - Get subcategories for category
GET    /api/categories/{id}/units/          - Get units for category
GET    /api/subcategories/                  - List all subcategories
GET    /api/subcategories/?category_id=1    - Filter by category
GET    /api/subcategories/{id}/             - Get subcategory details
GET    /api/units/                          - List all units
GET    /api/units/?category_id=1            - Filter by category
GET    /api/units/{id}/                     - Get unit details
```

---

## Error Responses

**400 Bad Request:**
```json
{
    "field_name": ["Error message"],
    "non_field_errors": ["General error message"]
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

## Success Response Codes
- `200 OK`: Successful GET, PUT requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests

---

## Quick Reference Examples

### Add a new product with purchase:
```bash
POST /api/shop-products/add_product/
{
    "shop_id": 1,
    "subcategory": 2,
    "quantity": 50,
    "buying_price_per_unit": 25.50,
    "payment_method": "CASH"
}
```

### Update selling price:
```bash
POST /api/shop-products/1/update_base_price/
{"base_price": 35.00}

POST /api/product-prices/update_unit_price/
{"product_id": 1, "unit_id": 2, "price": 28.50}
```

### Get products for a shop:
```bash
GET /api/shop-products/?shop_id=1
```

### Get transactions for buying:
```bash
GET /api/transactions/?transaction_type=BUY
```

### Filter subcategories by category:
```bash
GET /api/subcategories/?category_id=1
GET /api/categories/1/subcategories/
```

---

## Troubleshooting Common Issues

### 1. Unit-Based Price Addition Not Working
**Problem:** Getting errors when adding prices array
**Solution:**
- Ensure `unit_id` is an integer, not string
- Check that the unit exists and is allowed for the product category
- Use decimal string for price: `"30.00"` not `30.00`

**Correct Format:**
```json
"prices": [
    {"unit_id": 1, "price": "30.00"},  // ✅ Correct
    {"unit_id": "1", "price": 30.00}   // ❌ Wrong
]
```

### 2. Quantity Confusion for Hen/Egg
**Problem:** Unclear when to use quantity vs pieces_count
**Solution:**
- **For Eggs**: Use only `quantity` (number of eggs), set `pieces_count` to `null`
- **For Hen**: Use `quantity` for weight in kg, optionally use `pieces_count` for number of chickens

### 3. Stock Updates Not Reflecting
**Problem:** Stock doesn't update after transactions
**Solution:**
- The system automatically updates stock based on `quantity` field
- For hen: stock = weight in kg, pieces_count is just for tracking
- Check transaction was created successfully in response

### 4. Price Update Errors
**Problem:** Cannot update product prices
**Solution:**
- Use `/update_base_price/` to update the main selling price
- Use `/api/product-prices/update_unit_price/` for unit-specific prices
- Ensure the unit is valid for the product category

### 5. Transaction Creation Failures
**Problem:** Transactions fail with validation errors
**Solution:**
- All required fields must be provided including `payment_method`
- Check payment_method is valid: CASH, BANK, MOBILE, DUE
- For DUE payments, include due_date
- Ensure sufficient stock for sales

**Required Fields for Sales:**
```json
{
    "product_id": 1,
    "quantity": 10,
    "unit_id": 2,
    "selling_price_per_unit": 12.00,
    "payment_method": "CASH"  // ← This is required!
}
```

---

## Data Validation Notes

1. **Decimal Fields**: Use string format for prices: `"25.50"` not `25.50`
2. **Integer Fields**: Use integers for IDs: `1` not `"1"`
3. **Date Fields**: Use ISO format: `"2024-01-15"` for dates
4. **Null Values**: Use `null` not `""` for optional fields
5. **Payment Methods**: Valid options are `CASH`, `BANK`, `MOBILE`, `DUE`
