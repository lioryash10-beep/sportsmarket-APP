#include <stdio.h>

// פונקציה לחישוב המחיר החדש של שחקן (קנייה)
float calculate_price(float base_price, int current_supply) {
    float factor = 0.5;
    float new_price = base_price + (current_supply * factor);
    
    printf("[C Engine] Calculating BUY... Base: %.2f, Supply: %d -> New Price: %.2f\n", 
           base_price, current_supply, new_price);
           
    return new_price;
}

// פונקציה לחישוב מחיר המכירה (חדש!)
float calculate_sell_price(float base_price, int current_supply) {
    // מנגנון הגנה: אי אפשר למכור מניות אם אין שום היצע בשוק
    if (current_supply <= 0) {
        return base_price;
    }
    
    float factor = 0.5;
    // מחשבים את המחיר לפי המניה שהרגע החזרנו לשוק
    float sell_price = base_price + ((current_supply - 1) * factor);
    
    printf("[C Engine] Calculating SELL... Base: %.2f, Supply before sell: %d -> Return Price: %.2f\n", 
           base_price, current_supply, sell_price);
           
    return sell_price;
}