#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> d) {
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"a", 42}, {"b", 1337}, {"c", -1}, {"d", 5}}))) == (std::map<std::string,long>({{"a", 42}, {"b", 1337}, {"c", -1}, {"d", 5}})));
}
