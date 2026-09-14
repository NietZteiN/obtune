#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::string result = s;
    size_t pos = result.find('a');
    while (pos != std::string::npos) {
        result.erase(pos, 1);
        pos = result.find('a', pos);
    }
    pos = result.find('r');
    while (pos != std::string::npos) {
        result.erase(pos, 1);
        pos = result.find('r', pos);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("rpaar")) == ("p"));
}
