#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    text.push_back(value[0]);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("bcksrut"), ("q")) == ("bcksrutq"));
}
