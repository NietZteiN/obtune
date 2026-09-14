#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string n) {
    if (n.find('.') != std::string::npos) {
        return std::to_string(std::stoi(n) + 2.5);
    }
    return n;
}
int main() {
    auto candidate = f;
    assert(candidate(("800")) == ("800"));
}
