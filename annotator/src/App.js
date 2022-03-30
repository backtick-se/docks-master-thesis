import { useState, useEffect } from 'react'
import styled from 'styled-components'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'

const Center = styled('div')`
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: center;
`

const Wrapper = styled('div')`
    display: flex;
    width: 100vw;
    height: 100vh;
    flex-direction: column;
    overflow: hidden;
`

const TargetBox = styled('div')`
    display: flex;
    border: solid 1px rgba(0, 0, 0, 0.2);
    justify-content: space-between;
    padding: 1rem;
`

const Foot = styled('div')`
    display: flex;
    justify-content: center;
    padding: 1rem;
`

const Content = styled('div')`
    display: flex;
    flex-grow: 1;
    overflow: hidden;
`

const Section = styled('div')`
    display: flex;
    flex-grow: 1;
    padding: 1rem;
    overflow-y: scroll;
`

const Stats = styled(Section)`
    flex-direction: column;
`

const Features = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const Labels = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const LabelHead = styled('div')`
    display: flex;
    justify-content: space-between;
`

const Commit = styled('span')`
    display: flex;
    flex-direction: column;
    border: solid 1px rgba(0, 0, 0, 0.2);
    padding: 1rem;
    margin-bottom: 0.4rem;
`

const categories = [
    'fix-bugs',
    'new-features',
    'documentation',
    'non-functional',
]

const App = () => {
    const [data, setData] = useState(null)
    const [current, setCurrent] = useState(0)
    const [accepted, setAccepted] = useState([])
    const [rejected, setRejected] = useState([])
    const [docpage, setDocpage] = useState(0)
    const [selected, setSelected] = useState([])
    const [category, setCategory] = useState(null)

    // TODO: FIX new category selector

    useEffect(() => {
        if (data && data[current].category) {
            setCategory(data[current].category)
        } else {
            setCategory(null)
        }
    }, [data, current])

    const handleFile = (e) => {
        const fileReader = new FileReader()
        fileReader.readAsText(e.target.files[0], 'UTF-8')
        fileReader.onload = (e) => {
            setData(JSON.parse(e.target.result))
        }
    }

    const next = () => {
        setCurrent(current + 1)
    }

    const onSave = () => {
        const fileData = JSON.stringify(accepted)
        const blob = new Blob([fileData], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.download = 'data.json'
        link.href = url
        link.click()
    }

    const onAccept = () => {
        console.log(data[current])
        setAccepted([
            { ...data[current], target: selected, category: category },
            ...accepted,
        ])
        setDocpage(0)
        setSelected([])
        next()
    }

    const onReject = () => {
        setDocpage(0)
        setRejected([data[current], ...rejected])
        setSelected([])
        next()
    }

    const onNextDoc = () => {
        if (docpage + 1 < data[current].docs.length) {
            setDocpage(docpage + 1)
        }
    }

    const onPrevDoc = () => {
        if (docpage > 0) {
            setDocpage(docpage - 1)
        }
    }

    const onRadioChange = (e) => {
        if (selected.includes(data[current].docs[docpage][0])) {
            setSelected(
                selected.filter((s) => s !== data[current].docs[docpage][0])
            )
        } else {
            setSelected([...selected, data[current].docs[docpage][0]])
        }
    }

    const onCategoryChange = (e) => {
        setCategory(e.target.value)
    }

    return (
        <Wrapper>
            {data ? (
                <>
                    <Content>
                        <Stats>
                            <span>
                                <b>Accepted:</b> {accepted.length}
                            </span>
                            <span>
                                <b>Rejected:</b> {rejected.length}
                            </span>
                            <div style={{ flexGrow: 1 }} />
                            <button onClick={onSave}>Save</button>
                        </Stats>
                        {data[current] && (
                            <>
                                <Features>
                                    <LabelHead>
                                        <span>{data[current].number}</span>
                                        <span>
                                            {current + 1} / {data.length}
                                        </span>
                                    </LabelHead>
                                    <br />
                                    <TargetBox>
                                        <b>Select target:</b>
                                        {categories.map((cat) => (
                                            <label key={cat}>
                                                <input
                                                    type="radio"
                                                    name={cat}
                                                    checked={category === cat}
                                                    onClick={onCategoryChange}
                                                    value={cat}
                                                />
                                                {cat}
                                            </label>
                                        ))}
                                    </TargetBox>
                                    <br />
                                    <LabelHead>
                                        {data[current].labels.map((label) => (
                                            <span>{label.name}</span>
                                        ))}
                                    </LabelHead>

                                    {data[current].prediction && (
                                        <>
                                            <br />
                                            <b>Prediction:</b>
                                            <br />
                                            {data[current].prediction.map(
                                                (pred) => (
                                                    <span key={pred}>
                                                        {pred}
                                                    </span>
                                                )
                                            )}
                                        </>
                                    )}
                                    <h1>{data[current].title}</h1>
                                    <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                                        {data[current].body}
                                    </ReactMarkdown>
                                    <h2>Commits:</h2>
                                    {data[current].commits.map((commit, i) => (
                                        <>
                                            <Commit>
                                                <LabelHead>
                                                    <b>
                                                        {commit.commit.message}
                                                    </b>
                                                    <b
                                                        style={{
                                                            whiteSpace:
                                                                'nowrap',
                                                        }}
                                                    >{`+${commit.stats['additions']} -${commit.stats['deletions']}`}</b>
                                                </LabelHead>
                                                <br />
                                                {commit.files.map(
                                                    ({ filename }) => (
                                                        <>
                                                            <i>{filename}</i>
                                                            <br />
                                                        </>
                                                    )
                                                )}
                                            </Commit>
                                        </>
                                    ))}
                                </Features>
                                {data[current].docs && (
                                    <Labels>
                                        <LabelHead>
                                            <span>
                                                <input
                                                    type="radio"
                                                    name="docpage"
                                                    checked={selected.includes(
                                                        data[current].docs[
                                                            docpage
                                                        ][0]
                                                    )}
                                                    onClick={onRadioChange}
                                                    value={docpage}
                                                />
                                            </span>
                                            <span>
                                                <button onClick={onPrevDoc}>
                                                    Prev
                                                </button>
                                                &nbsp;
                                                <button onClick={onNextDoc}>
                                                    Next
                                                </button>
                                            </span>
                                            <span>
                                                {docpage} /{' '}
                                                {data[current].docs.length - 1}
                                            </span>
                                        </LabelHead>
                                        <br />
                                        {selected.map((s) => (
                                            <span>
                                                <b>Selected:</b> {s}
                                            </span>
                                        ))}
                                        <br />
                                        <LabelHead>
                                            <span>
                                                <b>Current:</b>{' '}
                                                {data[current].docs[docpage][0]}
                                            </span>
                                        </LabelHead>
                                        <ReactMarkdown>
                                            {data[current].docs[docpage][1]}
                                        </ReactMarkdown>
                                    </Labels>
                                )}
                            </>
                        )}
                    </Content>
                    <Foot>
                        <button onClick={onReject}>Reject Datapoint</button>
                        &nbsp;
                        <button onClick={onAccept}>Accept Selection</button>
                    </Foot>
                </>
            ) : (
                <Center>
                    <input type="file" onChange={handleFile} accept="json" />
                </Center>
            )}
        </Wrapper>
    )
}

export default App
