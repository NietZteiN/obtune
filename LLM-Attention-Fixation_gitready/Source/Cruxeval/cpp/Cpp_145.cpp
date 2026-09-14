#include<assert.h>
#include<bits/stdc++.h>
float f(float price, std::string product) {
    std::vector<std::string> inventory = {"olives", "key", "orange"};
    if (std::find(inventory.begin(), inventory.end(), product) == inventory.end()) {
        return price;
    } else {
        price *= 0.85;
        inventory.erase(std::remove(inventory.begin(), inventory.end(), product), inventory.end());
    }
    return price;
}
int main() {
    auto candidate = f;
    assert(candidate((8.5f), ("grapes")) == (8.5f));
}
