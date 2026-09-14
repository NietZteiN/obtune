#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string perc, std::string full) {
    std::string reply = "";
    int i = 0;
    while (i < full.size() && i < perc.size() && perc[i] == full[i]) {
        if (perc[i] == full[i]) {
            reply += "yes ";
        } else {
            reply += "no ";
        }
        i++;
    }
    return reply;
}
int main() {
    auto candidate = f;
    assert(candidate(("xabxfiwoexahxaxbxs"), ("xbabcabccb")) == ("yes "));
}
