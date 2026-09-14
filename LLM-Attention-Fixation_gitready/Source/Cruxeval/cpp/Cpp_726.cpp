#include<assert.h>
#include<bits/stdc++.h>
std::tuple<long, long> f(std::string text) {
    long ws = 0;
    for (char s : text) {
        if (isspace(s)) {
            ws += 1;
        }
    }
    return std::make_tuple(ws, text.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("jcle oq wsnibktxpiozyxmopqkfnrfjds")) == (std::make_tuple(2, 34)));
}
