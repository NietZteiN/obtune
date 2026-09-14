#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string p) {
    std::string result;
    auto arr = s.find(p);
    if (arr != std::string::npos) {
        int part_one = arr;
        int part_two = p.length();
        int part_three = s.length() - arr - p.length();

        if (part_one >= 2 && part_two <= 2 && part_three >= 2) {
            result = s.substr(0, part_one) + p + s.substr(part_one + part_two, part_three) + '#';
        } else {
            result = s;
        }
    } else {
        result = s;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("qqqqq"), ("qqq")) == ("qqqqq"));
}
