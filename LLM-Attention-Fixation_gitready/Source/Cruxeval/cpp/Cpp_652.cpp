#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    if (string.empty() || !isdigit(string[0])) {
        return "INVALID";
    }
    
    int cur = 0;
    for (int i = 0; i < string.length(); i++) {
        cur = cur * 10 + (string[i] - '0');
    }
    
    return std::to_string(cur);
}
int main() {
    auto candidate = f;
    assert(candidate(("3")) == ("3"));
}
