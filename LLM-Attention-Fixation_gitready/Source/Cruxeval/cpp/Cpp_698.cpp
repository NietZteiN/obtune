#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result;
    for (char x : text) {
        if (x != ')') {
            result += x;
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("(((((((((((d))))))))).))))(((((")) == ("(((((((((((d.((((("));
}
