#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> cart) {
    while(cart.size() > 5){
        cart.erase(std::prev(cart.end()));
    }
    return cart;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>())) == (std::map<long,long>()));
}
