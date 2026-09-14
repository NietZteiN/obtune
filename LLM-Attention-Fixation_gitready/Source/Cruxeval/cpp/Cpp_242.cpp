#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string book) {
    size_t pos = book.rfind(':');
    if (pos != std::string::npos) {
        std::string first = book.substr(0, pos);
        std::string second = book.substr(pos + 1);

        std::istringstream iss1(first);
        std::istringstream iss2(second);

        std::string lastWordFirst, firstWordSecond;

        iss1 >> std::noskipws >> lastWordFirst;
        iss2 >> firstWordSecond;

        if (lastWordFirst == firstWordSecond) {
            return f(first.substr(0, first.find_last_of(' ')) + ' ' + second);
        }
    }

    return book;
}
int main() {
    auto candidate = f;
    assert(candidate(("udhv zcvi nhtnfyd :erwuyawa pun")) == ("udhv zcvi nhtnfyd :erwuyawa pun"));
}
