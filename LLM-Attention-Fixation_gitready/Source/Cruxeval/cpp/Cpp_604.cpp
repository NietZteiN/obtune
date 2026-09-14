#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, std::string start) {
    return text.find(start) == 0;
}
int main() {
    auto candidate = f;
    assert(candidate(("Hello world"), ("Hello")) == (true));
}
