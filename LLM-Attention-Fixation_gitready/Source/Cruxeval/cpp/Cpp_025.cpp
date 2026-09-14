#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> d) {
    d.erase(std::prev(d.end()));
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"l", 1}, {"t", 2}, {"x:", 3}}))) == (std::map<std::string,long>({{"l", 1}, {"t", 2}})));
}
