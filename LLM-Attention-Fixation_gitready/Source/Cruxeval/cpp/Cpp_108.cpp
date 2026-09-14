#include<assert.h>
#include<bits/stdc++.h>
#include <variant>

using var_t = std::variant<int, std::map<std::string, long>, std::vector<long>>;

long f(var_t var) {
    long amount = 0;
    if (std::holds_alternative<std::map<std::string, long>>(var)) {
        amount = std::get<std::map<std::string, long>>(var).size();
    } 
    else if (std::holds_alternative<std::vector<long>>(var)) {
        amount = std::get<std::vector<long>>(var).size();
    }
    long nonzero = amount > 0 ? amount : 0;
    return nonzero;
}
int main() {
    auto candidate = f;
    assert(candidate((1)) == (0));
}
