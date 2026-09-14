#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> names) {
    if (names.empty()) {
        return "";
    }
    std::string smallest = names[0];
    for (size_t i = 1; i < names.size(); ++i) {
        if (names[i] < smallest) {
            smallest = names[i];
        }
    }
    names.erase(std::remove(names.begin(), names.end(), smallest), names.end());
    return smallest;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>())) == (""));
}
