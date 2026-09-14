#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string text) {
    std::string t = text;
    for (char i : text) {
        t.erase(std::remove(t.begin(), t.end(), i), t.end());
    }
    return std::to_string(t.size()) + text;
}
int main() {
    auto candidate = f;
    assert(candidate(("ThisIsSoAtrocious")) == ("0ThisIsSoAtrocious"));
}
