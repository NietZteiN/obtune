#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, std::string substring) {
    while (string.find(substring) == 0) {
        string = string.substr(substring.length());
    }
    return string;
}
int main() {
    auto candidate = f;
    assert(candidate((""), ("A")) == (""));
}
