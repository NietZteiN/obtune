#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string mess, std::string char_) {
    std::string::size_type pos = 0;
    while ((pos = mess.rfind(char_, pos)) != std::string::npos) {
        mess = mess.substr(0, pos + 1) + mess.substr(pos + char_.length());
    }
    return mess;
}
int main() {
    auto candidate = f;
    assert(candidate(("0aabbaa0b"), ("a")) == ("0aabbaa0b"));
}
