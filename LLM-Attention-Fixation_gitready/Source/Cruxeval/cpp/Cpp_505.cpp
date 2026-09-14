#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    while (!string.empty()) {
        if (isalpha(string.back())) {
            return string;
        }
        string.pop_back();
    }
    return string;
}
int main() {
    auto candidate = f;
    assert(candidate(("--4/0-209")) == (""));
}
