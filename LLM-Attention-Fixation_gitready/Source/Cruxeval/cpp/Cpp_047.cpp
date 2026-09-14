#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    int length = text.size();
    int half = length / 2;
    std::string encode = text.substr(0, half);
    if (text.substr(half) == encode) {
        return true;
    } else {
        return false;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("bbbbr")) == (false));
}
