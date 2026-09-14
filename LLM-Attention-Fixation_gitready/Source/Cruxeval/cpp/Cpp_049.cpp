#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (std::all_of(text.begin(), text.end(), isalnum)) {
        return std::accumulate(text.begin(), text.end(), std::string{}, [](std::string result, char c) {
            if (isdigit(c)) {
                return result + c;
            } else {
                return result;
            }
        });
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("816")) == ("816"));
}
