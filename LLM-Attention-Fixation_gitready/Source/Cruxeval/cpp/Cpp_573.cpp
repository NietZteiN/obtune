#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, std::string prefix) {
    if(string.find(prefix) == 0) {
        return string.substr(prefix.length());
    }
    return string;
}
int main() {
    auto candidate = f;
    assert(candidate(("Vipra"), ("via")) == ("Vipra"));
}
