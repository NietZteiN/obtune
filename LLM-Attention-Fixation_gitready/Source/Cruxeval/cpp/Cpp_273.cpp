#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string name) {
    std::string new_name = "";
    std::reverse(name.begin(), name.end());
    for (int i = 0; i < name.size(); i++) {
        char n = name[i];
        if (n != '.' && std::count(new_name.begin(), new_name.end(), '.') < 2) {
            new_name = n + new_name;
        } else {
            break;
        }
    }
    return new_name;
}
int main() {
    auto candidate = f;
    assert(candidate((".NET")) == ("NET"));
}
