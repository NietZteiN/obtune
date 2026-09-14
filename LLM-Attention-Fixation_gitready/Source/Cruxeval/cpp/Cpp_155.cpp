#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string ip, long n) {
    int i = 0;
    std::string out = "";
    for (char c : ip) {
        if (i == n) {
            out += '\n';
            i = 0;
        }
        i++;
        out += c;
    }
    return out;
}
int main() {
    auto candidate = f;
    assert(candidate(("dskjs hjcdjnxhjicnn"), (4)) == ("dskj\ns hj\ncdjn\nxhji\ncnn"));
}
