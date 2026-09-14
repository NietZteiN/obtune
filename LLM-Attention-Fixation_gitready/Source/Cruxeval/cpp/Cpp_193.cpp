#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    size_t count = std::count(string.begin(), string.end(), ':');
    size_t pos = string.find_last_of(':');
    return string.erase(pos, count - 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("1::1")) == ("1:1"));
}
