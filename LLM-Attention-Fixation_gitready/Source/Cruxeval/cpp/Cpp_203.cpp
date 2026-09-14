#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::string> f(std::map<std::string,std::string> d) {
    d.clear();
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>({{"a", "3"}, {"b", "-1"}, {"c", "Dum"}}))) == (std::map<std::string,std::string>()));
}
