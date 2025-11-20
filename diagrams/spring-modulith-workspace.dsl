workspace "Spring Modulith Example" "Architecture model for Spring Modulith example application" {

    model {
        user = person "Developer" "Application developer using Spring Modulith"
        
        springModulithApp = softwareSystem "Spring Modulith Example" "Example application demonstrating modular monolith architecture" {
            
            // Containers (modules as containers in a modular monolith)
            orderModule = container "Order Module" "Manages order lifecycle" "Java/Spring" {
                tags "Module"
                orderManagement = component "OrderManagement" "Public API for order operations" "Spring Service"
                orderInternal = component "OrderInternal" "Internal order logic" "Spring Service"
                order = component "Order" "Order domain model" "Entity"
                orderCompleted = component "OrderCompleted" "Order completion event" "Event"
            }
            
            inventoryModule = container "Inventory Module" "Manages inventory tracking" "Java/Spring" {
                tags "Module"
                inventoryManagement = component "InventoryManagement" "Public API for inventory" "Spring Service"
                inventoryInternal = component "InventoryInternal" "Internal inventory logic" "Spring Service"
                inventorySettings = component "InventorySettings" "Inventory configuration" "Configuration"
            }
        }
        
        // Relationships
        user -> springModulithApp "Uses"
        user -> orderModule "Creates orders in"
        
        // Module dependencies
        inventoryModule -> orderModule "Depends on" "Listens to order events"
        orderModule -> inventoryModule "Notifies"
        
        // Internal component relationships
        orderManagement -> order "Manages"
        orderInternal -> order "Processes"
        orderManagement -> orderCompleted "Publishes"
        
        inventoryManagement -> inventorySettings "Uses"
        inventoryInternal -> orderCompleted "Listens to"
    }

    views {
        systemContext springModulithApp "SystemContext" {
            include *
            autolayout lr
            description "System context diagram for Spring Modulith example application"
        }
        
        container springModulithApp "Containers" {
            include *
            autolayout lr
            description "Module-level view showing Order and Inventory modules"
        }
        
        component orderModule "OrderComponents" {
            include *
            autolayout lr
            description "Components within the Order module"
        }
        
        component inventoryModule "InventoryComponents" {
            include *
            autolayout lr
            description "Components within the Inventory module"
        }
        
        dynamic springModulithApp "OrderFlow" "Order processing flow" {
            user -> orderModule "1. Create order"
            orderModule -> inventoryModule "2. Publish OrderCompleted event"
            inventoryModule -> orderModule "3. Update inventory based on order"
            autolayout lr
        }
        
        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Module" {
                background #438dd5
                color #ffffff
            }
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
        }
        
        theme default
    }
}
