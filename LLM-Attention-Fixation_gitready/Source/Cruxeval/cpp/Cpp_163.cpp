#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string space_symbol, long size) {
    std::string spaces = "";
    for (long i = 0; i < size - text.length(); i++)
        spaces += space_symbol;
    return text + spaces;
}
int main() {
    auto candidate = f;
    assert(candidate(("w"), ("))"), (7)) == ("w))))))))))))"));
}
