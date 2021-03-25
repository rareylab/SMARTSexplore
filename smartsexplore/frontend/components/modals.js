import * as M from 'materialize-css/dist/js/materialize.min.js'

const Modal = {
    name: 'Modal',
    props: {
        id: String,
        buttonText: String,
    },
    template:`
    <!--Modal Trigger-->
    <a class="waves-effect waves-light btn modal-trigger" :href="'#' + id">{{ buttonText }}</a>

    <!-- Modal Structure -->
    <div :id="id" class="modal" ref="modal">
        <div class="modal-content">
            <slot></slot>
        </div>
        <div class="modal-footer">
            <a href="#!" class="modal-close waves-effect waves-green btn-flat">Close</a>
        </div>
    </div>
`,
    mounted() {
        this._modal = M.Modal.init(this.$refs.modal);
    },
    beforeUnmount() {
        this._modal.destroy();
    }
};



/**
 * The about button of the app, containing a modal that explains the application to the user.
 */
const AboutButton = {
    name: 'AboutButton',
    components: { Modal },
    template: `
    <modal id="about-modal" button-text="Learn more">
        <h4>About SMARTSexplore</h4>
        <p>
            SMARTSexplore is a web-based chemical pattern network analysis tool that allows
            comparison of available SMARTS-libraries and allows uploading of .smiles-files for
            matching with SMARTS.
        </p>
        <p>This tool was created by Inken Fender, Pia Pluemer and Simon Welker, 2021.</p>
    </modal>
`,
};


/**
 * The library info button of the app, containing references to the included SMARTS libraries.
 */
const InfoButton = {
    name: 'InfoButton',
    components: { Modal },
    template: `
    <modal id="info-modal" button-text="Info">
        <h4>References</h4>
        <ul class="collection">
            <li class="collection-item">BMS (Bristol-Myers Squibb): Pearce, B. C.; Sofia, M. J.; Good, A. C.; Drexler, D. M.; Stock, D. A. An empirical process for the design of high-throughput screening deck filters. J. Chem. Inf. Model. 2006, 46, 1060−1068., <a href="https://www.bms.com/de" target="_blank">https://www.bms.com/de</a></li>
            <li class="collection-item">Dundee: Brenk, R.; Schipani, A.; James, D.; Krasowski, A.; Gilbert, I. H.; Frearson, J.; Wyatt, P. G. Lessons learnt from assembling screening libraries for drug discovery for neglected diseases. ChemMedChem 2008, 3, 435−444</li>
            <li class="collection-item">Glaxo: Hann, M.; Hudson, B.; Lewell, X.; Lifely, R.; Miller, L.; Ramsden, N. Strategic Pooling of Compounds for High-Throughput Screening. J. Chem. Inf. Model. 1999, 39, 897−902.</li>
            <li class="collection-item">Inpharmatica: Inpharmatica Inc., <a href="http://www.inpharmatica.co.uk" target="_blank">http://www.inpharmatica.co.uk</a></li>
            <li class="collection-item">Lint: Blake, J. F. Identification and evaluation of molecular properties related to preclinical optimization and clinical fate. Med. Chem. (Sharjah, United Arab Emirates) 2005, 1, 649−655.</li>
            <li class="collection-item">Mlsmr: <a href="https://www.yumpu.com/en/document/view/12367541/mlsmr-excluded-functionality-filters-nih-molecular-libraries-" target="_blank">https://www.yumpu.com/en/document/view/12367541/mlsmr-excluded-functionality-filters-nih-molecular-libraries-</a> </li>
            <li class="collection-item">PAINS:  Baell, J. B., Holloway, G. A. New Substructure Filters for Removal of Pan Assay Interference Compounds (PAINS) from Screening Libraries and for their Exclusion in Bioassays, J Med Chem, 2010 , 53, <a href="https://pubs.acs.org/doi/10.1021/jm901137j" target="_blank">https://pubs.acs.org/doi/10.1021/jm901137j</a></li>
            <li class="collection-item">Smartscyp: Rydberg, P.; Gloriam, D. E.; Zaretzki, J.; Breneman, C.; Olsen, L. SMARTCyp: A 2D method for prediction of cytochrome P450-mediated drug metabolism. ACS Med. Chem. Lett. 2010, 1, 96−100.</li>
            <li class="collection-item">SureChEMBL: ToxAlerts: A Web Server of Structural Alerts for Toxic Chemicals and Compounds with Potential Adverse Reactions Iurii Sushko, Elena Salmina, Vladimir A. Potemkin, Gennadiy Poda, and Igor V. Tetko Journal of Chemical Information and Modeling 2012 52 (8), 2310-2316, <a href="https://www.surechembl.org/knowledgebase/169485-non-medchem-friendly-smarts" target="_blank">https://www.surechembl.org/knowledgebase/169485-non-medchem-friendly-smarts</a></li>
        </ul>
    </modal>
`,
};


export { Modal, AboutButton, InfoButton };
