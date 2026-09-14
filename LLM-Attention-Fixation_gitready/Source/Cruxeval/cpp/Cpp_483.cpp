#include <assert.h>
#include <bits/stdc++.h>

std::string f(std::string text, std::string delimiter) {
    std::istringstream iss(text);
    std::string token;
    std::string result;
    while (std::getline(iss, token, delimiter[0])) {
        result += token + " ";
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("a"), ("a")) == (" "));
}
