#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::vector<std::string> a{""};
    std::string b = "";
    for (char i : text) {
        if (!std::isspace(i)) {
            a.push_back(b);
            b = "";
        } else {
            b += i;
        }
    }
    return a.size();
}
int main() {
    auto candidate = f;
    assert(candidate(("       ")) == (1));
}
