using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        return text.All(char.IsLetterOrDigit);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wW의IV]HDJjhgK[dGIUlVO@Ess$coZkBqu[Ct")) == (false));
    }

}
