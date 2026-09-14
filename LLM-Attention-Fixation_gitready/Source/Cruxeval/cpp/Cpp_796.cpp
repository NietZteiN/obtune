#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string str, std::string toget) {
    if (str.find(toget) == 0) {
        return str.substr(toget.size());
    } else {
        return str;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("fnuiyh"), ("ni")) == ("fnuiyh"));
}
