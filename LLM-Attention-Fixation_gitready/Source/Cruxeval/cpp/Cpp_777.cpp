#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> names, std::string excluded) {
    for (int i = 0; i < names.size(); i++) {
        if (names[i].find(excluded) != std::string::npos) {
            size_t pos = names[i].find(excluded);
            names[i] = names[i].erase(pos, excluded.length());
        }
    }
    return names;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"avc  a .d e"})), ("")) == (std::vector<std::string>({(std::string)"avc  a .d e"})));
}
