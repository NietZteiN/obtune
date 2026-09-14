#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if(suffix.find("/") == 0) {
        return text + suffix.substr(1);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("hello.txt"), ("/")) == ("hello.txt"));
}
